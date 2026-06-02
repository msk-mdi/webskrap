"""Live bot-detection tests for WebSkrap's stealth features.

These drive a stealth-configured browser against public bot-detection demos and
assert that WebSkrap is not flagged. They require network access and real
third-party services, so they are opt-in:

    WEBSKRAP_LIVE=1 pytest tests/test_bot_detection.py

They are skipped by default (and in CI) because the services are slow and may
change their markup or scoring at any time. They only exercise public detection
demos meant for this purpose — no CAPTCHA solving or access-control bypass.

They pass with the patchright stealth driver (``driver="patchright"``), which is
a CDP-leak-free Playwright fork, run headed against the real Chrome channel:

- patchright hides the CDP ``Runtime.enable`` leak (``isAutomatedWithCDP``);
- headed mode clears headless-only behavioral signals;
- the real Chrome channel avoids FingerprintJS's anti-detect tampering signal
  that flags patchright's bundled Chromium;
- WebSkrap's own JS-surface patches and synthetic profile (viewport, locale,
  timezone, Accept-Language) are disabled so the browser's real fingerprint
  shows through instead of a spoofed one.

Requires Google Chrome installed on the host and the optional stealth extra
(``pip install webskrap[stealth]`` plus ``patchright install chromium``).
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

import pytest

from webskrap import SessionConfig, StealthConfig, WebSkrapClient

pytestmark = [pytest.mark.browser, pytest.mark.live]

# patchright is a CDP-leak-free Playwright fork; it is the stealth mechanism, so
# WebSkrap's own JS-surface patches are disabled to avoid reintroducing leaks.
# Headed mode is required: headless Chromium is flagged by behavioral signals
# regardless of CDP hiding. The real Chrome channel (not patchright's bundled
# Chromium) is required to clear FingerprintJS's anti-detect tampering signal, so
# Google Chrome must be installed on the host.
STEALTH = SessionConfig(
    driver="patchright",
    channel="chrome",
    headless=False,
    stealth=StealthConfig(enabled=False),
)


@pytest.fixture(autouse=True)
def _require_live() -> None:
    if not os.environ.get("WEBSKRAP_LIVE"):
        pytest.skip("set WEBSKRAP_LIVE=1 to run live bot-detection tests")


@asynccontextmanager
async def stealth_page():
    # Yield a stealth page, skipping if Playwright/browser is unavailable.
    client = WebSkrapClient(default_config=STEALTH)
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


async def test_fingerprintjs_web_scraping_demo() -> None:
    # FingerprintJS web-scraping demo must return flight prices, not block us.
    async with stealth_page() as page:
        await page.goto(
            "https://demo.fingerprint.com/web-scraping",
            wait_until="domcontentloaded",
            timeout=60_000,
        )
        await page.wait_for_timeout(8_000)
        await page.get_by_role("button", name="Search").click(timeout=8_000)
        await page.wait_for_timeout(6_000)
        result = await page.evaluate(
            """() => {
                const text = document.body.innerText;
                const blocked =
                    text.includes('access denied') ||
                    text.includes('request was blocked') ||
                    text.includes('bot visit detected');
                const flights = text.includes('$') || text.includes('Buy');
                return {blocked, flights};
            }"""
        )
    assert not result["blocked"], "FingerprintJS blocked us as a bot"
    assert result["flights"], "FingerprintJS: no flight data returned"


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


async def test_bot_sannysoft() -> None:
    # bot.sannysoft.com — no detection row may be marked failed.
    async with stealth_page() as page:
        await page.goto(
            "https://bot.sannysoft.com", wait_until="networkidle", timeout=60_000
        )
        await page.wait_for_timeout(4_000)
        failed = await page.evaluate(
            """() => {
                const failed = [];
                document.querySelectorAll('table tr').forEach(r => {
                    const cells = r.querySelectorAll('td');
                    if (cells.length >= 2 && (cells[1].className || '').includes('failed')) {
                        failed.push(cells[0].innerText.trim());
                    }
                });
                return failed;
            }"""
        )
    assert failed == [], f"Sannysoft failures: {', '.join(failed)}"


async def test_bot_incolumitas() -> None:
    # bot.incolumitas.com — only network/spec false positives are tolerated.
    known_acceptable = {"WEBDRIVER", "connectionRTT"}
    async with stealth_page() as page:
        await page.goto(
            "https://bot.incolumitas.com", wait_until="networkidle", timeout=60_000
        )
        await page.wait_for_timeout(13_000)
        failed = await page.evaluate(
            """() => {
                const text = document.body.innerText;
                const fails = text.match(/"(\\w+)":\\s*"FAIL"/g) || [];
                return fails.map(m => m.match(/"(\\w+)"/)[1]);
            }"""
        )
    unexpected = [name for name in failed if name not in known_acceptable]
    assert unexpected == [], f"Incolumitas unexpected failures: {', '.join(unexpected)}"


async def test_are_you_headless() -> None:
    # antoinevastel "are you headless" — must report not Chrome headless.
    async with stealth_page() as page:
        await page.goto(
            "https://arh.antoinevastel.com/bots/areyouheadless",
            wait_until="domcontentloaded",
            timeout=60_000,
        )
        await page.wait_for_timeout(5_000)
        text = await page.evaluate("() => document.body.innerText")
    assert "You are not Chrome headless" in text, "flagged as Chrome headless"


# CreepJS renders its automation signals as boolean rows inside a labelled
# block (e.g. "Headless | webDriverIsOn: false | ..."). A clean fingerprint has
# every Headless and Stealth signal false: not detected as headless, and no
# stealth/tampering lies (proxy, patched runtime, toString proxy, faked WebGL).
# The soft "Like Headless" heuristic is intentionally ignored — it reflects
# benign environment quirks (color scheme, missing experimental APIs).
_CREEPJS_EVAL = """() => {
    const blockFor = (label) => {
        let block = "";
        document.querySelectorAll('*').forEach(el => {
            if (el.children.length === 0 && (el.textContent || '').trim() === label) {
                const p = el.parentElement;
                if (p) block = (p.textContent || '').replace(/\\s+/g, ' ').trim();
            }
        });
        return block;
    };
    return {headless: blockFor('Headless'), stealth: blockFor('Stealth')};
}"""


async def test_creepjs() -> None:
    async with stealth_page() as page:
        await page.goto(
            "https://abrahamjuliot.github.io/creepjs/",
            wait_until="networkidle",
            timeout=60_000,
        )
        await page.wait_for_timeout(16_000)
        signals = await page.evaluate(_CREEPJS_EVAL)
    assert signals["headless"], "CreepJS Headless block did not render"
    assert signals["stealth"], "CreepJS Stealth block did not render"
    assert ": true" not in signals["headless"], (
        f"CreepJS flagged a headless signal: {signals['headless']}"
    )
    assert ": true" not in signals["stealth"], (
        f"CreepJS flagged a stealth/tampering signal: {signals['stealth']}"
    )
