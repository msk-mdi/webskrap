# WebSkrap

WebSkrap is an async-first Python scraping framework built on Playwright.

It provides coherent browser profiles, persistent browser sessions, resource routing, a CLI, and configurable browser hardening for data collection workflows that need realistic browser behavior.

!!! warning "Usage boundary"
    WebSkrap does not include CAPTCHA solving, login-wall bypassing, credential bypassing, or access-control circumvention. Use it only on targets you are allowed to access.

## Install

```bash
pip install webskrap
python -m playwright install chromium
```

## First Fetch

```python
import asyncio

from webskrap import WebSkrapClient


async def main() -> None:
    async with WebSkrapClient() as client:
        result = await client.fetch("https://example.com")
        print(result.status)
        print(result.title)


asyncio.run(main())
```

## Features

- Async Playwright lifecycle management.
- One-shot fetch helper for simple scripts.
- Persistent sessions with browser storage.
- Built-in desktop and mobile profiles.
- Custom profile support for locale, timezone, viewport, headers, and browser surfaces.
- Resource routing presets.
- CLI commands for fetches, profile inspection, and environment checks.

## Next Steps

- [Installation](getting-started/installation.md)
- [Quickstart](getting-started/quickstart.md)
- [Sessions](user-guide/sessions.md)
- [API Reference](api-reference.md)
