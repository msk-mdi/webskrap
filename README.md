# WebSkrap

WebSkrap is an async-first Python scraping framework built on Playwright. It provides coherent browser profiles, persistent sessions, resource routing, and configurable browser hardening for data collection workflows that need realistic browser behavior.

Repository: https://github.com/kacigaya/webskrap

WebSkrap does not include CAPTCHA solving, login-wall bypassing, credential bypassing, or access-control circumvention. Use it only on targets you are allowed to access.

## Install

```bash
pip install -e ".[dev]"
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
