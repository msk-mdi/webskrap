# Stealth

WebSkrap includes a configurable browser hardening layer.

The goal is coherent browser behavior: profile settings, headers, viewport, language, timezone, and selected JavaScript-visible browser surfaces should agree with each other.

!!! warning "Boundary"
    WebSkrap does not solve CAPTCHA challenges, bypass login walls, bypass credential checks, or circumvent access controls.

## Options

```python
from webskrap import SessionConfig, StealthConfig

config = SessionConfig(
    stealth=StealthConfig(
        enabled=True,
        patch_webdriver=True,
        patch_headless_user_agent=False,
        patch_window_metrics=False,
        patch_chrome_runtime=True,
        patch_permissions=True,
        patch_plugins=True,
        patch_webgl=True,
        patch_canvas=True,
        patch_hardware=True,
    )
)
```

Disable browser hardening:

```python
config = SessionConfig(stealth=StealthConfig(enabled=False))
```

## Patchright

Use the optional Patchright driver for CDP-aware detection surfaces:

```bash
pip install "webskrap[stealth]"
patchright install chromium
```

```python
from webskrap import SessionConfig, StealthConfig

config = SessionConfig(
    driver="patchright",
    channel="chrome",
    headless=False,
    stealth=StealthConfig(enabled=False),
)
```

Patchright works best with real Chrome, a persistent context, and no synthetic
JavaScript-surface patches. If `user_data_dir` is omitted, WebSkrap creates a
temporary persistent profile for Patchright sessions.

## Headless Patchright

Headless mode is more detectable than headed mode. For best-effort headless
stealth, opt in to targeted headless patches and prefer a stable profile:

```python
from pathlib import Path

from webskrap import SessionConfig, StealthConfig

config = SessionConfig(
    driver="patchright",
    channel="chrome",
    headless=True,
    user_data_dir=Path(".webskrap/headless-profile"),
    stealth=StealthConfig(
        enabled=True,
        patch_headless_user_agent=True,
        patch_window_metrics=True,
        patch_webdriver=True,
        patch_webgl=False,
        patch_canvas=False,
    ),
)
```

`patch_headless_user_agent` removes `HeadlessChrome` from JavaScript-visible
browser strings and can apply coherent profile headers. `patch_window_metrics`
fills common headless gaps in window and screen dimensions. Keep WebGL and canvas
patches off unless a target proves they help.

## Practical Guidance

- Reuse persistent sessions when realistic continuity matters.
- Keep locale, timezone, and languages coherent.
- Prefer an installed browser channel such as `chrome` when testing headed behavior.
- Treat headless stealth as best-effort; headed Patchright remains the strict mode.
- Avoid randomizing every request; incoherent changes can look less realistic.
