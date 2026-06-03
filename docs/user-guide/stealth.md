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

## Headless Patchright

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

## Practical Guidance

- Reuse persistent sessions when realistic continuity matters.
- Keep locale, timezone, and languages coherent.
- Prefer an installed browser channel such as `chrome` when testing headed behavior.
- Treat headless stealth as best-effort; headed Patchright remains the strict mode.
- Avoid randomizing every request; incoherent changes can look less realistic.
