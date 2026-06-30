# WebSkrap

Async-first Python scraping on Playwright. Coherent profiles, persistent sessions, resource routing, and Patchright-powered stealth.

> **⚠ Usage boundary** — WebSkrap does not include CAPTCHA solving, login-wall bypassing, credential bypassing, or access-control circumvention. Use it only on targets you are allowed to access.

## Install

```bash
pip install webskrap
webskrap install
```

## First fetch

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

## Explore

- [Installation](/docs/getting-started/installation)
- [Quickstart](/docs/getting-started/quickstart)
- [Client](/docs/user-guide/client)
- [Sessions](/docs/user-guide/sessions)
- [Profiles](/docs/user-guide/profiles)
- [Stealth](/docs/user-guide/stealth)
- [CLI](/docs/user-guide/cli)
- [API Reference](/docs/api-reference)
