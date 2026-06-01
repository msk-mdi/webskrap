"""Live bot-detection tests for WebSkrap's stealth features.

These drive a stealth-configured browser against public bot-detection demos and
assert that WebSkrap is not flagged. They require network access and real
third-party services, so they are opt-in:

    WEBSKRAP_LIVE=1 pytest tests/test_bot_detection.py

They are skipped by default (and in CI) because the services are slow and may
change their markup or scoring at any time. They only exercise public detection
demos meant for this purpose — no CAPTCHA solving or access-control bypass.

Current status: WebSkrap drives vanilla Chromium over the DevTools Protocol and
applies JavaScript-surface patches via StealthConfig. That clears basic
fingerprint checks (BrowserScan) but the CDP channel itself stays detectable
(`isAutomatedWithCDP == true`), which trips CDP-aware and challenge-based
detectors. Hiding CDP requires a patched browser binary, which WebSkrap does not
ship. Toggling headless was verified to make no difference. The four tests below
are therefore marked xfail(strict=True): they document the gap and will flip to
XPASS — failing the run — if stealth ever improves enough to beat them.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

import pytest

from webskrap import SessionConfig, StealthConfig, WebSkrapClient

pytestmark = [pytest.mark.browser, pytest.mark.live]

STEALTH = SessionConfig(headless=True, stealth=StealthConfig(enabled=True))


@pytest.fixture(autouse=True)
def _require_live() -> None:
    if not os.environ.get("WEBSKRAP_LIVE"):
        pytest.skip("set WEBSKRAP_LIVE=1 to run live bot-detection tests")


@asynccontextmanager
async def stealth_page():
    # Yield a stealth page, skipping if Playwright/browser is unavailable.
    client = WebSkrapClient()
    try:
        await client.start()
        session = await client.session("bot-detect", config=STEALTH, profile="desktop-chrome")
        page = await session.context.new_page()
    except Exception as exc:  # noqa: BLE001 - environment guard, re-raised as skip
        await client.close()
        pytest.skip(f"Playwright browser unavailable: {exc}")
    try:
        yield page
    finally:
        await client.close()


@pytest.mark.xfail(
    strict=True,
    reason="reCAPTCHA v3 does not return a human-range score for CDP-driven Chromium",
)
async def test_recaptcha_v3() -> None:
    # reCAPTCHA v3 score must be >= 0.7 (human range).
    async with stealth_page() as page:
        await page.goto(
            "https://recaptcha-demo.appspot.com/recaptcha-v3-request-scores.php",
            wait_until="domcontentloaded",
            timeout=60_000,
        )
        await page.wait_for_timeout(8_000)
        score = await page.evaluate(
            """() => {
                const m = document.body.innerText.match(/"score":\\s*(\\d+\\.\\d+)/);
                return m ? parseFloat(m[1]) : null;
            }"""
        )
    assert score is not None, "could not extract reCAPTCHA v3 score"
    assert score >= 0.7, f"reCAPTCHA v3 score too low: {score}"


@pytest.mark.xfail(
    strict=True,
    reason="Turnstile managed challenge does not auto-issue a token for CDP-driven Chromium",
)
async def test_cloudflare_turnstile_non_interactive() -> None:
    # Cloudflare Turnstile (managed/non-interactive) must auto-issue a token.
    async with stealth_page() as page:
        await page.goto(
            "https://2captcha.com/demo/cloudflare-turnstile",
            wait_until="domcontentloaded",
            timeout=60_000,
        )
        await page.wait_for_timeout(10_000)
        token = await page.evaluate(
            """() => {
                const el = document.querySelector(
                    'input[name="cf-turnstile-response"]'
                );
                return el ? el.value : "";
            }"""
        )
    assert token and len(token) > 20, f"Turnstile did not pass non-interactively (token={token!r})"


async def test_browserscan_bot_detection() -> None:
    # BrowserScan must report 0 abnormal checks.
    async with stealth_page() as page:
        await page.goto(
            "https://www.browserscan.net/bot-detection",
            wait_until="networkidle",
            timeout=60_000,
        )
        await page.wait_for_timeout(5_000)
        result = await page.evaluate(
            """() => {
                const text = document.body.innerText;
                return {
                    normal: (text.match(/Normal/g) || []).length,
                    abnormal: (text.match(/Abnormal/g) || []).length,
                };
            }"""
        )
    assert result["abnormal"] == 0, (
        f"BrowserScan: {result['abnormal']} abnormal, {result['normal']} normal"
    )


@pytest.mark.xfail(
    strict=True,
    reason="FingerprintJS web-scraping demo withholds results from CDP-driven Chromium",
)
async def test_fingerprintjs_web_scraping_demo() -> None:
    # FingerprintJS web-scraping demo must not block us as a bot.
    async with stealth_page() as page:
        await page.goto(
            "https://demo.fingerprint.com/web-scraping",
            wait_until="domcontentloaded",
            timeout=60_000,
        )
        await page.wait_for_timeout(8_000)
        try:
            await page.click("button:has-text('Search')", timeout=5_000)
            await page.wait_for_timeout(5_000)
        except Exception:  # noqa: BLE001 - button is optional, layout may vary
            pass
        result = await page.evaluate(
            """() => {
                const text = document.body.innerText;
                const blocked =
                    text.includes('request was blocked') ||
                    text.includes('bot visit detected');
                const flights =
                    text.includes('Price per adult') || text.includes('$');
                return {blocked, flights};
            }"""
        )
    assert not result["blocked"], "FingerprintJS blocked us as a bot"
    assert result["flights"], "FingerprintJS: no flight data returned"


@pytest.mark.xfail(
    strict=True,
    reason="deviceandbrowserinfo flags isAutomatedWithCDP; CDP channel is detectable",
)
async def test_device_and_browser_info_behavioral() -> None:
    # deviceandbrowserinfo.com behavioral detection: isBot must be false.
    async with stealth_page() as page:
        await page.goto(
            "https://deviceandbrowserinfo.com/are_you_a_bot",
            wait_until="domcontentloaded",
            timeout=60_000,
        )
        await page.wait_for_timeout(8_000)
        result = await page.evaluate(
            """() => {
                const text = document.body.innerText;
                const signals = {};
                ['isBot', 'hasWebdriverTrue', 'isHeadlessChrome',
                 'isAutomatedWithCDP', 'isPlaywright'].forEach(p => {
                    const m = text.match(
                        new RegExp('"' + p + '":\\\\s*(true|false)')
                    );
                    if (m) signals[p] = m[1] === 'true';
                });
                return {isBot: signals.isBot ?? null, signals};
            }"""
        )
    assert result["isBot"] is False, f"detected as bot; signals: {result['signals']}"
