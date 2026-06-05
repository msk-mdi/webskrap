<p align="center">
  <img src="assets/webskrap-logo.png" alt="WebSkrap logo" width="200">
</p>

<h1 align="center">WebSkrap</h1>

<p align="center">
   <strong>Async-first Python scraping framework built on Playwright.</strong><br>
   <em>It provides coherent browser profiles, persistent sessions, resource routing, and Patchright-powered stealth for data collection workflows that need realistic browser behavior.</em>
</p>

WebSkrap does not include CAPTCHA solving, login-wall bypassing, credential bypassing, or access-control circumvention. Use it only on targets you are allowed to access.

Documentation: https://kacigaya.github.io/webskrap/

## Install

```bash
pip install webskrap
python -m playwright install chromium
```

## Quickstart

```python
import asyncio

from webskrap import WebSkrapClient


async def main() -> None:
    async with WebSkrapClient() as client:
        result = await client.fetch("https://example.com")
        print(result.status)
        print(result.title)
        print(result.text[:200])


asyncio.run(main())
```

## Persistent session

```python
import asyncio
from pathlib import Path

from webskrap import SessionConfig, WebSkrapClient


async def main() -> None:
    config = SessionConfig(
        user_data_dir=Path(".webskrap/sessions/shop"),
        headless=True,
    )

    async with WebSkrapClient() as client:
        session = await client.session("shop", config=config, profile="desktop-chrome")
        first = await session.fetch("https://example.com")
        second = await session.fetch("https://example.com/account")
        print(first.final_url, second.final_url)


asyncio.run(main())
```

## Headed browser

Use a persistent session when you want the browser to stay open.

```python
import asyncio
from pathlib import Path

from webskrap import SessionConfig, WebSkrapClient


async def main() -> None:
    config = SessionConfig(
        headless=False,
        user_data_dir=Path(".webskrap/dev-session"),
    )

    async with WebSkrapClient() as client:
        session = await client.session("dev", config=config)
        page = await session.context.new_page()
        await page.goto("https://example.com", wait_until="domcontentloaded")

        input("Press Enter to close browser...")


asyncio.run(main())
```

## Human-like clicks

Use `human_click` when a manual interaction should include visible-element waits, scrolling,
short pauses, and mouse movement before the click.

```python
page = await session.context.new_page()
await page.goto("https://example.com", wait_until="domcontentloaded")
await session.human_click(page, "label[for='radio1']")
```

Enable the cursor hint in a headed browser when you want to see a red dot follow the
automated mouse movement. Re-enable it after navigation if you still need it.

```python
await session.enable_cursor_hint(page)
await session.human_click(page, "label[for='radio1']")
await session.disable_cursor_hint(page)
```

Example for a headed Chrome session with a French desktop profile:

```python
import asyncio
from pathlib import Path

from webskrap import BrowserProfile, SessionConfig, Viewport, WebSkrapClient


async def main() -> None:
    config = SessionConfig(
        headless=False,
        channel="chrome",
        user_data_dir=Path(".webskrap/example"),
        navigation_timeout_ms=90_000,
        default_timeout_ms=90_000,
        slow_mo_ms=50,
        launch_args=[
            "--start-maximized",
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
        ],
    )
    profile = BrowserProfile(
        name="fr-desktop",
        viewport=Viewport(width=1440, height=900),
        screen=Viewport(width=1440, height=900),
        locale="fr-FR",
        timezone_id="Europe/Paris",
        navigator_languages=["fr-FR", "fr", "en-US", "en"],
    )

    async with WebSkrapClient() as client:
        session = await client.session("example", config=config, profile=profile)
        page = await session.context.new_page()
        await page.goto("https://example.com", wait_until="domcontentloaded")

        input("Press Enter to close browser...")


asyncio.run(main())
```

## Custom profile

```python
from webskrap import BrowserProfile, Viewport

profile = BrowserProfile(
    name="workstation",
    viewport=Viewport(width=1440, height=900),
    screen=Viewport(width=1440, height=900),
    locale="en-US",
    timezone_id="Europe/Paris",
)
```

## Session options

```python
from pathlib import Path

from webskrap import ProxyConfig, ResourcePolicy, SessionConfig

config = SessionConfig(
    browser="chromium",
    channel="chrome",
    headless=False,
    user_data_dir=Path(".webskrap/session"),
    storage_state=None,
    proxy=ProxyConfig(server="http://127.0.0.1:8080"),
    resource_policy=ResourcePolicy.LITE,
    ignore_https_errors=True,
    java_script_enabled=True,
    service_workers="allow",
    timeout_ms=30_000,
    navigation_timeout_ms=90_000,
    default_timeout_ms=90_000,
    slow_mo_ms=50,
    launch_args=[
        "--start-maximized",
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-first-run",
        "--no-default-browser-check",
    ],
)
```

`resource_policy` values:

- `ResourcePolicy.ALL`: allow all resources.
- `ResourcePolicy.LITE`: block images, fonts, and media.
- `ResourcePolicy.DOCUMENTS`: block images, fonts, media, and stylesheets.

## Profile options

```python
from webskrap import BrowserProfile, Viewport

profile = BrowserProfile(
    name="fr-desktop",
    user_agent=None,
    viewport=Viewport(width=1440, height=900),
    screen=Viewport(width=1440, height=900),
    locale="fr-FR",
    timezone_id="Europe/Paris",
    device_scale_factor=1,
    is_mobile=False,
    has_touch=False,
    color_scheme="light",
    reduced_motion="no-preference",
    extra_http_headers={},
    navigator_languages=["fr-FR", "fr", "en-US", "en"],
)
```

## Patchright stealth

The default `playwright` driver is detectable by CDP-aware bot detectors because
the DevTools Protocol `Runtime.enable` call leaks. For maximum stealth, switch to
the [`patchright`](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) driver, a
CDP-leak-free Playwright fork, and let the browser's real fingerprint show through.
WebSkrap does not inject JavaScript stealth patches.

```bash
pip install "webskrap[stealth]"
patchright install chromium
```

```python
from webskrap import SessionConfig

config = SessionConfig(
    driver="patchright",
    channel="chrome",          # real Chrome beats anti-detect tampering checks
    headless=False,            # headed clears headless-only behavioral signals
)
```

With this configuration WebSkrap passes reCAPTCHA v3 (human score), Cloudflare
Turnstile (non-interactive), BrowserScan, the FingerprintJS web-scraping demo,
and deviceandbrowserinfo behavioral detection. See
[tests/test_bot_detection.py](tests/test_bot_detection.py) (run with
`WEBSKRAP_LIVE=1`). The `patchright` driver needs Google Chrome installed and the
`stealth` extra; without a `user_data_dir` it uses a throwaway persistent profile,
which patchright requires for full stealth.

### Headless patchright

Headed patchright is the strongest stealth mode. For best-effort headless runs,
prefer real Chrome plus a stable persistent profile.

```python
from pathlib import Path

from webskrap import SessionConfig

config = SessionConfig(
    driver="patchright",
    channel="chrome",
    headless=True,
    user_data_dir=Path(".webskrap/headless-profile"),
)
```

Headless mode is inherently more detectable than headed mode. WebSkrap keeps the
browser surfaces native instead of spoofing them with JavaScript, because broad
fingerprint patches can look like tampering.

Headless Chrome has no physical display, so it otherwise reports an 800x600
screen with zero `outerWidth`/`outerHeight`, an obvious headless tell. For
chromium headless runs WebSkrap configures a virtual screen at launch
(`--screen-info`, `--window-size`, `--window-position`), giving coherent
`screen`/`window` metrics without JavaScript spoofing. It defaults to 1920x1080;
override with `headless_screen=Viewport(width=..., height=...)` or disable with
`headless_screen=None`.

## CLI

```bash
webskrap profiles
webskrap doctor
webskrap fetch https://example.com --profile desktop-chrome
webskrap fetch https://example.com --headed --screenshot example.png
webskrap fetch https://example.com --driver patchright --channel chrome --headed
```

## Performance benchmarks

WebSkrap is a browser-automation framework, so these benchmarks measure what it
actually does: resource routing, session reuse, and concurrent fetching. They run
against a local HTTP server that serves a synthetic page referencing many delayed
sub-resources (images, stylesheets, media). No external sites are contacted, so
results are deterministic. Numbers below are from a single machine and will vary
with hardware; run them yourself with `python benchmarks.py`.

### Resource routing (full page load with delayed assets)

| Policy      | Time (ms) | vs ALL |
|-------------|:---------:|:------:|
| `DOCUMENTS` |  156.98   | 0.58x  |
| `LITE`      |  169.42   | 0.62x  |
| `ALL`       |  271.23   | 1.0x   |

Blocking images, fonts, and media (`LITE`) cuts load time ~38%; also dropping
stylesheets (`DOCUMENTS`) reaches ~42%.

### Session reuse

| Mode                  | Time (ms) | vs warm |
|-----------------------|:---------:|:-------:|
| Warm session reuse    |  215.74   |  1.0x   |
| Cold launch per fetch |  411.68   |  1.91x  |

Reusing a persistent session avoids per-fetch browser/context startup, roughly
2x faster than launching cold each time.

### Concurrency

Fetching 8 pages per batch from one session averages ~109 ms per page.

> Benchmarks average 20+ navigations after warm-up. See
> [benchmarks.py](benchmarks.py) for methodology.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
```
