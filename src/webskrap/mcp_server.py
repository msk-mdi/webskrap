"""Model Context Protocol server exposing WebSkrap over stdio.

Run with ``webskrap-mcp`` (after ``pip install webskrap[mcp]``) or
``python -m webskrap.mcp_server``. Point an MCP client (Claude Desktop, Claude
Code, ...) at that command to drive scraping through the tools below.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from webskrap.client import WebSkrapClient, WebSkrapError
from webskrap.models import SessionConfig, shape_fetch_result
from webskrap.parsing import (
    parse_resource_policy,
    parse_wait_until,
    parse_webrtc_ip_handling_policy,
)
from webskrap.profiles import get_profile

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - optional dependency
    msg = "the MCP server requires the optional dependency: pip install webskrap[mcp]"
    raise WebSkrapError(msg) from exc

mcp = FastMCP("webskrap")


@mcp.tool()
async def fetch(
    url: str,
    profile: str = "desktop-chrome",
    wait_until: str = "domcontentloaded",
    resource_policy: str = "all",
    timeout_ms: float = 30_000,
    max_chars: int = 20_000,
) -> dict[str, Any]:
    """Fetch a URL with a standard Playwright browser and return page data.

    Args:
        url: The URL to load.
        profile: Bundled profile (desktop-chrome, desktop-edge, mobile-chrome).
        wait_until: commit, domcontentloaded, load, or networkidle.
        resource_policy: all, lite (block images/fonts/media), or documents.
        timeout_ms: Navigation timeout in milliseconds.
        max_chars: Maximum characters of page HTML to return.
    """
    config = SessionConfig(
        navigation_timeout_ms=timeout_ms,
        resource_policy=parse_resource_policy(resource_policy),
    )
    async with WebSkrapClient() as client:
        result = await client.fetch(
            url,
            profile=get_profile(profile),
            config=config,
            wait_until=parse_wait_until(wait_until),
            timeout_ms=timeout_ms,
        )
    return shape_fetch_result(result, max_chars)


@mcp.tool()
async def stealth_fetch(
    url: str,
    profile: str = "desktop-chrome",
    channel: str = "chrome",
    headless: bool = True,
    user_data_dir: str | None = None,
    patchright_context_profile: bool = False,
    reduce_fingerprint_surface: bool = False,
    mask_headless_user_agent: bool = False,
    webrtc_ip_handling_policy: str | None = None,
    timeout_ms: float = 90_000,
    max_chars: int = 20_000,
) -> dict[str, Any]:
    """Fetch a URL with the Patchright stealth driver (CDP-leak-free).

    Requires the optional stealth extra: pip install webskrap[stealth] and
    patchright install chromium. Prefer headless=False with channel="chrome"
    for the strictest anti-bot path.

    Args:
        url: The URL to load.
        profile: Bundled profile applied when patchright_context_profile is set.
        channel: Browser channel, e.g. chrome.
        headless: Run headless. Headed is more robust against detection.
        user_data_dir: Persistent browser profile directory.
        patchright_context_profile: Apply locale/timezone/media profile metadata.
        reduce_fingerprint_surface: Disable WebGL and canvas readback via flags.
        mask_headless_user_agent: Rewrite the HeadlessChrome UA token to Chrome.
        webrtc_ip_handling_policy: Chromium WebRTC ICE policy, e.g.
            disable_non_proxied_udp.
        timeout_ms: Navigation timeout in milliseconds.
        max_chars: Maximum characters of page HTML to return.
    """
    config = SessionConfig(
        driver="patchright",
        channel=channel,
        headless=headless,
        user_data_dir=Path(user_data_dir) if user_data_dir else None,
        navigation_timeout_ms=timeout_ms,
        patchright_context_profile=patchright_context_profile,
        reduce_fingerprint_surface=reduce_fingerprint_surface,
        mask_headless_user_agent=mask_headless_user_agent,
        webrtc_ip_handling_policy=parse_webrtc_ip_handling_policy(webrtc_ip_handling_policy),
    )
    async with WebSkrapClient() as client:
        result = await client.fetch(
            url,
            profile=get_profile(profile),
            config=config,
            timeout_ms=timeout_ms,
        )
    return shape_fetch_result(result, max_chars)


@mcp.tool()
async def doctor() -> dict[str, Any]:
    """Check that Playwright and Chromium are installed and can launch."""
    try:
        from playwright.async_api import async_playwright
    except Exception as exc:  # noqa: BLE001 - report any import failure
        return {"ok": False, "message": f"Playwright import failed: {exc}"}

    try:
        manager = async_playwright()
        playwright = await manager.start()
        browser = await playwright.chromium.launch(headless=True)
        await browser.close()
        await playwright.stop()
    except Exception as exc:  # noqa: BLE001 - report any launch failure
        return {
            "ok": False,
            "message": f"Chromium did not launch: {exc}",
            "hint": "Run: python -m playwright install chromium",
        }

    return {"ok": True, "message": "Playwright and Chromium are ready."}


def main() -> None:
    """Entry point for the ``webskrap-mcp`` console script (stdio transport)."""
    mcp.run()


if __name__ == "__main__":
    main()
