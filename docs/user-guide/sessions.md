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

## Persistent Storage

Set `user_data_dir` to keep cookies, local storage, and browser profile state between runs.

```python
config = SessionConfig(user_data_dir=Path(".webskrap/profile"))
```

## Common Options

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
