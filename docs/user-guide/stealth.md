# Stealth

WebSkrap's stealth path is the optional Patchright driver.

Patchright is a CDP-leak-free Playwright fork. WebSkrap does not inject
JavaScript fingerprint patches; it relies on real browser behavior, persistent
contexts, and coherent profile settings instead.

!!! warning "Boundary"
    WebSkrap does not solve CAPTCHA challenges, bypass login walls, bypass credential checks, or circumvent access controls.

## Patchright

Use the optional Patchright driver for CDP-aware detection surfaces:

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

Patchright works best with real Chrome and a persistent context. If
`user_data_dir` is omitted, WebSkrap creates a temporary persistent profile for
Patchright sessions.

## Headless patchright

Headless mode is more detectable than headed mode. For best-effort headless
stealth, prefer real Chrome and a stable profile:

```python
from pathlib import Path

from webskrap import SessionConfig

config = SessionConfig(
    driver="patchright",
    channel="chrome",
    headless=True,
    user_data_dir=Path(".webskrap/headless-profile"),
)
```

WebSkrap intentionally keeps headless browser surfaces native instead of spoofing
them with JavaScript. Broad fingerprint patches often become tampering signals.

Headless Chrome has no physical display, so screen and window metrics
(`screen.width`, `window.outerWidth`, ...) otherwise leak as headless tells,
defaulting to an 800x600 screen with zero outer dimensions. For chromium headless
runs WebSkrap configures a virtual screen at launch via browser flags
(`--screen-info`, `--window-size`, `--window-position`), so the page reports
coherent display metrics. This is a real browser-level screen, not JavaScript
spoofing, so it does not register as tampering. The default is 1920x1080; set
`headless_screen` to a `Viewport` to change it, or to `None` to disable:

```python
from webskrap import SessionConfig, Viewport

config = SessionConfig(
    driver="patchright",
    channel="chrome",
    headless=True,
    headless_screen=Viewport(width=1366, height=768),
)
```

The other headless tell that survives patchright is the user agent: headless
Chrome stamps `HeadlessChrome` into `navigator.userAgent` and the worker UA
(including `SharedWorker`, which runs in its own process). Set
`mask_headless_user_agent=True` to rewrite it to `Chrome`. WebSkrap probes the
real UA once, then applies the cleaned value via the browser's own
`--user-agent` override at launch. The setting is process wide, covering the page, every
worker, and request headers, with native client hints left intact. It is off by
default so headless stays honestly headless unless you opt in.

```python
config = SessionConfig(
    driver="patchright",
    channel="chrome",
    headless=True,
    headless_screen=Viewport(width=1366, height=768),
    mask_headless_user_agent=True,
)
```

With a simulated screen and a masked UA, a headless chromium run clears the live
bot-detection suite (`tests/test_bot_detection.py`) that otherwise requires
headed mode.

## Practical guidance

- Reuse persistent sessions when realistic continuity matters.
- Keep locale, timezone, and languages coherent.
- Prefer an installed browser channel such as `chrome` when testing headed behavior.
- Treat headless stealth as best-effort; headed Patchright remains the strict mode.
- Avoid randomizing every request; incoherent changes can look less realistic.
