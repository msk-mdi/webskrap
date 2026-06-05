# Sessions

Sessions keep a browser context open across multiple requests.

```python
import asyncio
from pathlib import Path

from webskrap import SessionConfig, WebSkrapClient


async def main() -> None:
    config = SessionConfig(
        user_data_dir=Path(".webskrap/session"),
        headless=True,
    )

    async with WebSkrapClient() as client:
        session = await client.session("default", config=config)
        first = await session.fetch("https://example.com")
        second = await session.fetch("https://example.com/account")
        print(first.status, second.status)


asyncio.run(main())
```

## Persistent storage

Set `user_data_dir` to keep cookies, local storage, and browser profile state between runs.

```python
config = SessionConfig(user_data_dir=Path(".webskrap/profile"))
```

## Human-like clicks

Sessions expose `human_click` for interactions that should behave more like a manual click
than a direct Playwright `page.click`.

```python
async with WebSkrapClient() as client:
    session = await client.session("default")
    page = await session.context.new_page()
    await page.goto("https://example.com", wait_until="domcontentloaded")
    await session.human_click(page, "label[for='radio1']")
```

Pass `human=False` to use the same helper while delegating directly to Playwright.

```python
await session.human_click(page, "label[for='radio1']", human=False, timeout=5_000)
```

Enable the cursor hint in a headed browser to show a red dot at the automated mouse
position while debugging. The hint is scoped to the current page document, so enable it
again after navigation if needed.

```python
await session.enable_cursor_hint(page)
await session.human_click(page, "label[for='radio1']")
await session.disable_cursor_hint(page)
```

## Common options

```python
config = SessionConfig(
    browser="chromium",
    channel="chrome",
    headless=False,
    navigation_timeout_ms=90_000,
    default_timeout_ms=90_000,
    slow_mo_ms=50,
    launch_args=[
        "--start-maximized",
        "--no-first-run",
        "--no-default-browser-check",
    ],
)
```
