---
name: webskrap
description: Use when writing Python scraping or browser automation code with WebSkrap, including async fetches, persistent sessions, browser profiles, resource policies, stealth configuration, screenshots, CLI usage, and safety boundaries.
---

# WebSkrap

WebSkrap is an async-first Python scraping framework built on Playwright for realistic browser sessions, coherent profiles, resource controls, and structured fetch results.

## Use This Skill When

- Writing Python code that fetches pages with `webskrap`.
- Keeping browser state across requests with persistent sessions.
- Configuring browser profiles, locale, timezone, viewport, proxy, or resource policy.
- Taking screenshots or debugging with a headed browser.
- Using the `webskrap` CLI.

## Core Workflow

Install WebSkrap and the Playwright browser before running examples:

```bash
pip install webskrap
python -m playwright install chromium
```

Use `WebSkrapClient` as an async context manager. Use `client.fetch()` for one-shot page fetches. Use `client.session()` when browser state, cookies, local storage, human-like clicks, or a headed browser should persist across actions.

## Common Patterns

One-shot fetch:

```python
import asyncio

from webskrap import WebSkrapClient


async def main() -> None:
    async with WebSkrapClient() as client:
        result = await client.fetch("https://example.com")
        print(result.status)
        print(result.final_url)
        print(result.title)
        print(result.text[:200])


asyncio.run(main())
```

Persistent session:

```python
import asyncio
from pathlib import Path

from webskrap import SessionConfig, WebSkrapClient


async def main() -> None:
    config = SessionConfig(user_data_dir=Path(".webskrap/session"), headless=True)

    async with WebSkrapClient() as client:
        session = await client.session("default", config=config)
        first = await session.fetch("https://example.com")
        second = await session.fetch("https://example.com/account")
        print(first.status, second.status)


asyncio.run(main())
```

Custom profile:

```python
from webskrap import BrowserProfile, Viewport

profile = BrowserProfile(
    name="fr-desktop",
    viewport=Viewport(width=1440, height=900),
    screen=Viewport(width=1440, height=900),
    locale="fr-FR",
    timezone_id="Europe/Paris",
    navigator_languages=["fr-FR", "fr", "en-US", "en"],
)
```

Resource policy:

```python
from webskrap import ResourcePolicy, SessionConfig

config = SessionConfig(resource_policy=ResourcePolicy.LITE)
```

CLI fetch:

```bash
webskrap doctor
webskrap profiles
webskrap fetch https://example.com --profile desktop-chrome --screenshot example.png
```

## Safety Boundaries

Do not use WebSkrap to solve CAPTCHA challenges, bypass login walls, bypass credential checks, or circumvent access controls. Keep examples limited to targets the user is allowed to access.

## Reference Docs

- `docs/llms.txt`: compact LLM-facing package summary.
- `docs/getting-started/quickstart.md`: quick examples for fetches, sessions, and CLI usage.
- `docs/user-guide/client.md`: `WebSkrapClient`, `fetch()`, and `FetchResult`.
- `docs/user-guide/sessions.md`: persistent sessions and human-like clicks.
- `docs/user-guide/profiles.md`: built-in and custom browser profiles.
- `docs/user-guide/resource-policy.md`: resource blocking policies.
- `docs/user-guide/stealth.md`: browser hardening configuration and boundaries.
- `docs/api-reference.md`: public API reference.
