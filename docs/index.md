---
hide:
  - navigation
  - toc
---

<div class="ws-hero" markdown>

# WebSkrap

<p class="ws-tagline">Async-first Python scraping framework built on Playwright, with coherent browser profiles, persistent sessions, resource routing, and Patchright support for workflows that need realistic browser behavior.</p>

<div class="ws-cta" markdown>
[Get started](getting-started/installation.md){ .md-button .md-button--primary }
[Quickstart](getting-started/quickstart.md){ .md-button }
[View on GitHub](https://github.com/kacigaya/webskrap){ .md-button }
</div>

</div>

!!! warning "Usage boundary"
    WebSkrap does not include CAPTCHA solving, login-wall bypassing, credential bypassing, or access-control circumvention. Use it only on targets you are allowed to access.

## Install

```bash
pip install webskrap
python -m playwright install chromium
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

## Features

<div class="grid cards" markdown>

-   :material-lightning-bolt:{ .lg .middle } Async by design

    ---

    Fully async Playwright lifecycle management with a one-shot `fetch` helper for simple scripts.

    [:octicons-arrow-right-24: Client](user-guide/client.md)

-   :material-account-box:{ .lg .middle } Coherent profiles

    ---

    Built-in desktop and mobile profiles, plus custom locale, timezone, viewport, headers, and browser surfaces.

    [:octicons-arrow-right-24: Profiles](user-guide/profiles.md)

-   :material-database-sync:{ .lg .middle } Persistent sessions

    ---

    Keep browser storage across runs so authenticated and stateful flows stay realistic.

    [:octicons-arrow-right-24: Sessions](user-guide/sessions.md)

-   :material-shield-lock:{ .lg .middle } Stealth and routing

    ---

    Patchright support and resource routing presets to shape browser behavior.

    [:octicons-arrow-right-24: Stealth](user-guide/stealth.md)

-   :material-console:{ .lg .middle } CLI included

    ---

    Run fetches, inspect profiles, and check your environment straight from the terminal.

    [:octicons-arrow-right-24: CLI](user-guide/cli.md)

-   :material-api:{ .lg .middle } Typed API

    ---

    Annotated signatures and a generated reference for every public surface.

    [:octicons-arrow-right-24: API Reference](api-reference.md)

</div>
