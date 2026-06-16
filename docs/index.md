---
hide:
  - navigation
  - toc
---

<div class="ws-hero" markdown>

<img class="ws-logo" src="assets/webskrap-logo.png" alt="WebSkrap logo">

# WebSkrap

<p class="ws-tagline">Async-first Python scraping on Playwright. Coherent profiles, persistent sessions, and resource routing.</p>

<div class="ws-cta" markdown>
[Get started](getting-started/installation.md){ .md-button .md-button--primary }
[Quickstart](getting-started/quickstart.md){ .md-button }
[View on GitHub](https://github.com/kacigaya/webskrap){ .md-button }
</div>

<div class="ws-terminal">
  <span class="ws-terminal__dots"><i></i><i></i><i></i></span>
  <code class="ws-terminal__cmd"><span class="ws-prompt">$</span> pip install webskrap</code>
  <button type="button" class="ws-copy" data-ws-copy="pip install webskrap" aria-label="Copy install command">
    <svg class="ws-copy__icon ws-copy__copy" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <rect x="9" y="9" width="13" height="13" rx="2"></rect>
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
    </svg>
    <svg class="ws-copy__icon ws-copy__check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M20 6 9 17l-5-5"></path>
    </svg>
  </button>
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
