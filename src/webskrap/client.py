from __future__ import annotations

import time
from collections.abc import Mapping
from pathlib import Path
from random import uniform
from typing import Any, Literal
from uuid import uuid4

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

from webskrap.models import BrowserProfile, FetchResult, ResourcePolicy, SessionConfig
from webskrap.profiles import get_profile
from webskrap.stealth import apply_stealth

WaitUntil = Literal["commit", "domcontentloaded", "load", "networkidle"]

_CURSOR_HINT_ENABLE_SCRIPT = """
() => {
    const markerId = "__webskrap_cursor_hint";
    if (window.__webskrapCursorHint) {
        return;
    }

    const marker = document.createElement("div");
    marker.id = markerId;
    marker.setAttribute("aria-hidden", "true");
    Object.assign(marker.style, {
        position: "fixed",
        left: "0px",
        top: "0px",
        width: "12px",
        height: "12px",
        borderRadius: "50%",
        background: "rgba(255, 0, 0, 0.9)",
        border: "2px solid rgba(255, 255, 255, 0.95)",
        boxShadow: "0 0 0 1px rgba(0, 0, 0, 0.35), 0 0 12px rgba(255, 0, 0, 0.65)",
        transform: "translate(-50%, -50%)",
        pointerEvents: "none",
        zIndex: "2147483647",
    });

    const move = (event) => {
        marker.style.left = `${event.clientX}px`;
        marker.style.top = `${event.clientY}px`;
    };

    document.documentElement.appendChild(marker);
    window.__webskrapCursorHint = { marker, move };
    window.addEventListener("mousemove", move, true);
}
"""

_CURSOR_HINT_DISABLE_SCRIPT = """
() => {
    const state = window.__webskrapCursorHint;
    if (!state) {
        return;
    }
    window.removeEventListener("mousemove", state.move, true);
    state.marker.remove();
    delete window.__webskrapCursorHint;
}
"""


class WebSkrapError(RuntimeError):
    pass


class WebSkrapSession:
    def __init__(
        self,
        *,
        name: str,
        context: BrowserContext,
        config: SessionConfig,
        profile: BrowserProfile,
        browser: Browser | None = None,
    ) -> None:
        self.name = name
        self.context = context
        self.config = config
        self.profile = profile
        self.browser = browser
        self._closed = False

    async def __aenter__(self) -> WebSkrapSession:
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        await self.close()

    async def fetch(
        self,
        url: str,
        *,
        wait_until: WaitUntil = "domcontentloaded",
        screenshot: bool | str | Path = False,
        timeout_ms: float | None = None,
    ) -> FetchResult:
        self._ensure_open()
        started = time.perf_counter()
        page = await self.context.new_page()
        try:
            _configure_page_timeouts(page, self.config)
            response = await page.goto(
                url,
                wait_until=wait_until,
                timeout=timeout_ms or self.config.navigation_timeout_ms,
            )
            title = await page.title()
            text = await page.content()
            screenshot_path = await _maybe_screenshot(page, screenshot)
            cookies = await self.context.cookies()
            elapsed_ms = (time.perf_counter() - started) * 1000
            status = response.status if response else None
            headers = dict(response.headers) if response else {}
            return FetchResult(
                url=url,
                final_url=page.url,
                status=status,
                ok=status is not None and 200 <= status < 400,
                headers=headers,
                text=text,
                title=title,
                cookies=cookies,
                timings={"elapsed_ms": elapsed_ms},
                screenshot_path=screenshot_path,
            )
        finally:
            await page.close()

    async def human_click(
        self,
        page: Page,
        selector: str,
        *,
        human: bool = True,
        **click_options: Any,
    ) -> None:
        self._ensure_open()
        if not human:
            await page.click(selector, **click_options)
            return

        locator = page.locator(selector)
        timeout = click_options.get("timeout")
        await locator.wait_for(state="visible", timeout=timeout)
        await locator.scroll_into_view_if_needed(timeout=timeout)

        if click_options.get("strict") is True and await locator.count() != 1:
            msg = f"strict mode expected one element for selector: {selector}"
            raise WebSkrapError(msg)

        box = await locator.bounding_box(timeout=timeout)
        if box is None:
            msg = f"could not find a visible bounding box for selector: {selector}"
            raise WebSkrapError(msg)

        x, y = _human_click_point(box, click_options.get("position"))
        if click_options.get("trial"):
            return

        await page.wait_for_timeout(uniform(80, 220))

        start_x = x + uniform(-160, 160)
        start_y = y + uniform(-90, 90)
        await page.mouse.move(start_x, start_y, steps=1)
        await page.mouse.move(
            x + uniform(-8, 8),
            y + uniform(-6, 6),
            steps=max(4, min(18, int((box["width"] + box["height"]) / 10))),
        )
        await page.wait_for_timeout(uniform(40, 140))

        mouse_options = _mouse_click_options(click_options)
        modifiers = click_options.get("modifiers") or []
        for modifier in modifiers:
            await page.keyboard.down(modifier)
        try:
            await page.mouse.click(x, y, **mouse_options)
        finally:
            for modifier in reversed(modifiers):
                await page.keyboard.up(modifier)

    async def enable_cursor_hint(self, page: Page) -> None:
        self._ensure_open()
        await page.evaluate(_CURSOR_HINT_ENABLE_SCRIPT)

    async def disable_cursor_hint(self, page: Page) -> None:
        self._ensure_open()
        await page.evaluate(_CURSOR_HINT_DISABLE_SCRIPT)

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        await self.context.close()
        if self.browser is not None:
            await self.browser.close()

    def _ensure_open(self) -> None:
        if self._closed:
            msg = f"session '{self.name}' is closed"
            raise WebSkrapError(msg)


class WebSkrapClient:
    def __init__(
        self,
        *,
        default_config: SessionConfig | None = None,
        profiles: Mapping[str, BrowserProfile] | None = None,
    ) -> None:
        self.default_config = default_config or SessionConfig()
        self.profiles = dict(profiles or {})
        self._playwright_manager = None
        self._playwright: Playwright | None = None
        self._sessions: dict[str, WebSkrapSession] = {}

    async def __aenter__(self) -> WebSkrapClient:
        await self.start()
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        await self.close()

    async def start(self) -> None:
        if self._playwright is not None:
            return
        self._playwright_manager = async_playwright()
        self._playwright = await self._playwright_manager.start()

    async def close(self) -> None:
        for session in list(self._sessions.values()):
            await session.close()
        self._sessions.clear()
        if self._playwright is not None:
            await self._playwright.stop()
        self._playwright_manager = None
        self._playwright = None

    async def fetch(
        self,
        url: str,
        *,
        profile: str | BrowserProfile | None = None,
        config: SessionConfig | None = None,
        wait_until: WaitUntil = "domcontentloaded",
        screenshot: bool | str | Path = False,
        timeout_ms: float | None = None,
    ) -> FetchResult:
        name = f"_single_{uuid4().hex}"
        session = await self.session(name, config=config, profile=profile)
        try:
            return await session.fetch(
                url,
                wait_until=wait_until,
                screenshot=screenshot,
                timeout_ms=timeout_ms,
            )
        finally:
            await session.close()
            self._sessions.pop(name, None)

    async def session(
        self,
        name: str,
        *,
        config: SessionConfig | None = None,
        profile: str | BrowserProfile | None = None,
    ) -> WebSkrapSession:
        if name in self._sessions:
            return self._sessions[name]
        await self.start()
        resolved_config = config or self.default_config
        resolved_profile = self._resolve_profile(profile)
        session = await self._create_session(name, resolved_config, resolved_profile)
        self._sessions[name] = session
        return session

    def _resolve_profile(self, profile: str | BrowserProfile | None) -> BrowserProfile:
        if isinstance(profile, BrowserProfile):
            return profile
        if profile in self.profiles:
            return self.profiles[profile].model_copy(deep=True)
        return get_profile(profile)

    async def _create_session(
        self,
        name: str,
        config: SessionConfig,
        profile: BrowserProfile,
    ) -> WebSkrapSession:
        if self._playwright is None:
            msg = "client is not started"
            raise WebSkrapError(msg)

        browser_type = getattr(self._playwright, config.browser)
        context_options = config.context_options(profile)

        if config.user_data_dir is not None:
            config.user_data_dir.mkdir(parents=True, exist_ok=True)
            context = await browser_type.launch_persistent_context(
                str(config.user_data_dir),
                **config.launch_options(),
                **context_options,
            )
            browser = None
        else:
            browser = await browser_type.launch(**config.launch_options())
            context = await browser.new_context(**context_options)

        context.set_default_timeout(config.default_timeout_ms)
        context.set_default_navigation_timeout(config.navigation_timeout_ms)

        if config.resource_policy != ResourcePolicy.ALL:
            await context.route("**/*", _resource_route_handler(config.resource_policy))
        if config.stealth.enabled:
            await apply_stealth(context, profile, config.stealth)

        return WebSkrapSession(
            name=name,
            context=context,
            config=config,
            profile=profile,
            browser=browser,
        )


def _resource_route_handler(policy: ResourcePolicy):
    blocked = {
        ResourcePolicy.LITE: {"image", "font", "media"},
        ResourcePolicy.DOCUMENTS: {"image", "font", "media", "stylesheet"},
    }[policy]

    async def handle(route) -> None:
        if route.request.resource_type in blocked:
            await route.abort()
        else:
            await route.continue_()

    return handle


def _configure_page_timeouts(page: Page, config: SessionConfig) -> None:
    page.set_default_timeout(config.default_timeout_ms)
    page.set_default_navigation_timeout(config.navigation_timeout_ms)


def _human_click_point(
    box: dict[str, float],
    position: dict[str, float] | None,
) -> tuple[float, float]:
    if position is not None:
        return box["x"] + position["x"], box["y"] + position["y"]

    jitter_x = min(box["width"] * 0.2, 6)
    jitter_y = min(box["height"] * 0.2, 6)
    return (
        box["x"] + box["width"] / 2 + uniform(-jitter_x, jitter_x),
        box["y"] + box["height"] / 2 + uniform(-jitter_y, jitter_y),
    )


def _mouse_click_options(click_options: dict[str, Any]) -> dict[str, Any]:
    mouse_options: dict[str, Any] = {}
    if "button" in click_options:
        mouse_options["button"] = click_options["button"]
    if "click_count" in click_options:
        mouse_options["click_count"] = click_options["click_count"]
    if "delay" in click_options:
        mouse_options["delay"] = click_options["delay"]
    return mouse_options


async def _maybe_screenshot(page: Page, screenshot: bool | str | Path) -> Path | None:
    if not screenshot:
        return None
    path = (
        Path(f"webskrap-{int(time.time() * 1000)}.png")
        if screenshot is True
        else Path(screenshot)
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    await page.screenshot(path=str(path), full_page=True)
    return path
