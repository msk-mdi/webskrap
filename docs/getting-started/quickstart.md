# Quickstart

## One-Shot Fetch

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

## Keep A Headed Browser Open

Use a session when you want the browser to remain open for inspection.

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

## Human-like Clicks

Use `human_click` for manual interactions that should wait for the element, scroll it into
view, pause briefly, move the mouse, and then click.

```python
page = await session.context.new_page()
await page.goto("https://example.com", wait_until="domcontentloaded")
await session.human_click(page, "label[for='radio1']")
```

## CLI Fetch

```bash
webskrap fetch https://example.com
webskrap fetch https://example.com --headed --screenshot example.png
```
