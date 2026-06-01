<p align="center">
  <img src="assets/webskrap-logo.png" alt="WebSkrap logo" width="200">
</p>

<h1 align="center">WebSkrap</h1>

<p align="center">
   <strong>Async-first Python scraping framework built on Playwright.</strong><br>
   <em>It provides coherent browser profiles, persistent sessions, resource routing, and configurable browser hardening for data collection workflows that need realistic browser behavior.</em>
</p>

WebSkrap does not include CAPTCHA solving, login-wall bypassing, credential bypassing, or access-control circumvention. Use it only on targets you are allowed to access.

Documentation: https://kacigaya.github.io/webskrap/

## Install

```bash
pip install webskrap
python -m playwright install chromium
```

## Quick Start

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

## Persistent Session

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

## Headed Browser

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

## Custom Profile

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

## Session Options

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

## Profile Options

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
    hardware_concurrency=8,
    device_memory=8,
    webgl_vendor="Google Inc. (Intel)",
    webgl_renderer="ANGLE (Intel, Intel(R) Iris(TM) Plus Graphics, OpenGL 4.1)",
)
```

## Stealth Options

```python
from webskrap import SessionConfig, StealthConfig

config = SessionConfig(
    stealth=StealthConfig(
        enabled=True,
        patch_webdriver=True,
        patch_chrome_runtime=True,
        patch_permissions=True,
        patch_plugins=True,
        patch_webgl=True,
        patch_canvas=True,
        patch_hardware=True,
    )
)
```

## CLI

```bash
webskrap profiles
webskrap doctor
webskrap fetch https://example.com --profile desktop-chrome
webskrap fetch https://example.com --headed --screenshot example.png
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
```
