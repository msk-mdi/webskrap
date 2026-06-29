---
name: webskrap
description: Use when writing, debugging, documenting, or reviewing Python scraping and browser automation code with WebSkrap. Covers async fetches, persistent sessions, Playwright/Patchright drivers, browser profiles, resource policies, screenshots, proxies, timeouts, CLI usage, MCP server usage, and safe examples that avoid CAPTCHA solving, login-wall bypassing, credential bypassing, or access-control circumvention.
---

# WebSkrap

WebSkrap is an async-first Python scraping framework built on Playwright for realistic browser sessions, coherent profiles, resource controls, and structured fetch results.

## Start Here

Before giving detailed guidance, check the local docs when available:

- `docs/getting-started/quickstart.md`: first examples for fetches, sessions, clicks, screenshots, and CLI.
- `docs/user-guide/client.md`: `WebSkrapClient`, one-shot fetches, timeouts, screenshots, and `FetchResult`.
- `docs/user-guide/sessions.md`: persistent sessions, headed debugging, page workflows, and human-like clicks.
- `docs/user-guide/profiles.md`: built-in and custom browser profiles.
- `docs/user-guide/resource-policy.md`: resource blocking presets.
- `docs/user-guide/stealth.md`: Patchright, headless behavior, WebRTC policy, and fingerprint-surface controls.
- `docs/user-guide/cli.md`: `webskrap` command examples.
- `docs/user-guide/mcp.md`: optional MCP server setup and tool arguments.
- `docs/api-reference.md`: generated public API reference.

## Guardrails

- Do not add CAPTCHA solving, login-wall bypassing, credential bypassing, or access-control circumvention.
- Keep examples limited to public pages, local servers, or targets the user is allowed to access.
- Do not commit cookies, storage state, proxy credentials, or persistent browser data such as `.webskrap/`.
- Prefer typed public APIs exported by `webskrap`; avoid reaching into private helpers except in tests.
- Use `async with WebSkrapClient()` unless you are explicitly demonstrating manual `start()` / `close()`.

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
    print(result.status, result.final_url, result.title)
    print(result.text[:200])


asyncio.run(main())
```

Fetch with a screenshot and custom navigation wait:

```python
result = await client.fetch(
    "https://example.com",
    wait_until="load",
    screenshot="example.png",
    timeout_ms=60_000,
)
print(result.screenshot_path)
```

Persistent session with storage between runs:

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

Manual page workflow:

```python
async with WebSkrapClient() as client:
    session = await client.session("debug", config=SessionConfig(headless=False))
    page = await session.context.new_page()
    await page.goto("https://example.com", wait_until="domcontentloaded")
    await session.human_click(page, "a")
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

Proxy and timeout configuration:

```python
from webskrap import ProxyConfig, ResourcePolicy, SessionConfig

config = SessionConfig(
    proxy=ProxyConfig(server="http://127.0.0.1:8080"),
    resource_policy=ResourcePolicy.LITE,
    navigation_timeout_ms=90_000,
    default_timeout_ms=90_000,
)
```

Patchright headed stealth path:

```bash
pip install "webskrap[stealth]"
patchright install chromium
```

```python
from webskrap import SessionConfig

config = SessionConfig(
    driver="patchright",
    channel="chrome",
    headless=False,
)
```

Use Patchright for CDP-aware detection surfaces. It uses a persistent context for full stealth; if `user_data_dir` is omitted, WebSkrap creates a temporary persistent profile. WebSkrap does not inject JavaScript stealth patches, so let the real browser fingerprint show through.

Headless Patchright is best-effort. Prefer real Chrome, a stable `user_data_dir`, a coherent virtual screen, and the browser-level user-agent mask only when the user asks for headless stealth:

```python
from pathlib import Path

from webskrap import SessionConfig, Viewport

config = SessionConfig(
    driver="patchright",
    channel="chrome",
    headless=True,
    user_data_dir=Path(".webskrap/headless-profile"),
    headless_screen=Viewport(width=1366, height=768),
    mask_headless_user_agent=True,
)
```

For fingerprint-statistics or WebRTC leak-test pages, use native browser controls instead of JavaScript patches:

```python
config = SessionConfig(
    driver="patchright",
    channel="chrome",
    headless=True,
    patchright_context_profile=True,
    reduce_fingerprint_surface=True,
    webrtc_ip_handling_policy="disable_non_proxied_udp",
)
```

These settings do not hide the page's normal remote address and do not normalize unrelated high-entropy surfaces such as fonts, battery, TLS/session metadata, or installed browser features.

CLI fetch:

```bash
webskrap doctor
webskrap profiles
webskrap fetch https://example.com --profile desktop-chrome --screenshot example.png
webskrap fetch https://example.com --output page.html --resource-policy lite
webskrap fetch https://example.com --driver patchright --channel chrome --headed
```

MCP server:

```bash
pip install "webskrap[mcp]"
python -m playwright install chromium
webskrap-mcp
```

Use `stealth_fetch` only after installing both MCP and stealth extras:

```bash
pip install "webskrap[mcp,stealth]"
patchright install chromium
```

## Validation

For code changes, run the focused checks relevant to the edit:

```bash
pytest -q
ruff check .
```

Use `WEBSKRAP_LIVE=1 pytest -q -m live` only for opt-in third-party bot-detection tests. Those tests are slower and may fail when public demos change.
