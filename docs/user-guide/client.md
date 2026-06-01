# Client

`WebSkrapClient` owns the Playwright lifecycle.

Use it as an async context manager:

```python
import asyncio

from webskrap import WebSkrapClient


async def main() -> None:
    async with WebSkrapClient() as client:
        result = await client.fetch("https://example.com")
        print(result.status)


asyncio.run(main())
```

## One-Shot Fetch

`client.fetch()` creates a temporary browser session, opens the page, collects the response data, then closes that temporary session.

```python
result = await client.fetch(
    "https://example.com",
    wait_until="domcontentloaded",
    screenshot="example.png",
)
```

Use `client.session()` when you want to keep browser state or keep a headed browser open.

## FetchResult

`FetchResult` includes:

- `url`
- `final_url`
- `status`
- `ok`
- `headers`
- `text`
- `title`
- `cookies`
- `timings`
- `screenshot_path`
