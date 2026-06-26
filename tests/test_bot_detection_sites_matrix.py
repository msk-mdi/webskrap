"""Live smoke tests for every active URL in bot_detection_test_sites.md.

These tests intentionally validate reachability and basic page rendering, not
site-specific verdicts. Detailed detectors such as SannySoft, CreepJS, and
BrowserScan are covered by tests/test_bot_detection.py.
"""

from __future__ import annotations

import os
import re
from contextlib import suppress
from pathlib import Path

import pytest

from webskrap import ProxyConfig, SessionConfig, Viewport, WebSkrapClient

pytestmark = [pytest.mark.browser, pytest.mark.live]

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "bot_detection_test_sites.md"

URL_RE = re.compile(r"https?://[^\s|]+")


def _live_proxy() -> ProxyConfig | None:
    server = os.environ.get("WEBSKRAP_LIVE_PROXY")
    if not server:
        return None
    return ProxyConfig(
        server=server,
        username=os.environ.get("WEBSKRAP_LIVE_PROXY_USERNAME"),
        password=os.environ.get("WEBSKRAP_LIVE_PROXY_PASSWORD"),
    )


def _live_config(headless: bool) -> SessionConfig:
    return SessionConfig(
        driver="patchright",
        channel=os.environ.get("WEBSKRAP_BROWSER_CHANNEL", "chrome"),
        headless=headless,
        user_data_dir=Path(
            os.environ.get(
                "WEBSKRAP_LIVE_HEADLESS_PROFILE_DIR" if headless else "WEBSKRAP_LIVE_PROFILE_DIR",
                ".webskrap/live-headless-profile" if headless else ".webskrap/live-stealth-profile",
            )
        ),
        headless_screen=Viewport(width=1366, height=768) if headless else None,
        mask_headless_user_agent=headless,
        proxy=_live_proxy(),
        webrtc_ip_handling_policy="disable_non_proxied_udp",
    )


def _active_sites() -> list[str]:
    urls: list[str] = []
    for line in MATRIX.read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5 or cells[0].lower() != "active":
            continue
        match = URL_RE.search(cells[2])
        if match and match.group(0) not in urls:
            urls.append(match.group(0))
    return urls


@pytest.fixture(autouse=True)
def _require_live() -> None:
    if not os.environ.get("WEBSKRAP_LIVE"):
        pytest.skip("set WEBSKRAP_LIVE=1 to run live bot-detection site matrix")


async def _probe_site(context: object, url: str) -> str | None:
    page = await context.new_page()
    try:
        response = await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        with suppress(Exception):
            await page.wait_for_function(
                "() => (document.body?.innerText || '').trim().length > 40",
                timeout=8_000,
            )
        title = await page.title()
        body_text = await page.evaluate("() => document.body ? document.body.innerText : ''")
        final_url = page.url
    except Exception as exc:  # noqa: BLE001 - aggregate live-site failures
        return f"{url}: {type(exc).__name__}: {str(exc).splitlines()[0]}"
    finally:
        await page.close()

    status = response.status if response else None
    if status is None:
        return f"{url}: no navigation response"
    if status >= 400:
        return f"{url}: HTTP {status} at {final_url!r} ({title!r})"
    if len(body_text.strip()) <= 40:
        return f"{url}: page rendered too little text"
    return None


async def _probe_sites_with_config(name: str, config: SessionConfig) -> list[str]:
    client = WebSkrapClient(default_config=config)
    try:
        await client.start()
        session = await client.session(
            f"bot-detection-sites-{name}",
            config=config,
            profile="desktop-chrome",
        )
    except Exception as exc:  # noqa: BLE001 - environment guard, re-raised as skip
        await client.close()
        pytest.skip(f"Playwright browser unavailable: {exc}")

    failures: list[str] = []
    try:
        for url in _active_sites():
            failure = await _probe_site(session.context, url)
            if failure:
                failures.append(failure)
    finally:
        await client.close()
    return failures


async def test_active_bot_detection_sites_load_headed_and_headless() -> None:
    results = {
        "headed": await _probe_sites_with_config("headed", _live_config(headless=False)),
        "headless": await _probe_sites_with_config("headless", _live_config(headless=True)),
    }
    failures = [
        f"{mode}: {failure}" for mode, mode_failures in results.items() for failure in mode_failures
    ]

    assert failures == [], "Live site matrix failures:\n" + "\n".join(failures)
