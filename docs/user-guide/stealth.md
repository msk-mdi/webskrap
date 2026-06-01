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

## Practical Guidance

- Reuse persistent sessions when realistic continuity matters.
- Keep locale, timezone, and languages coherent.
- Prefer an installed browser channel such as `chrome` when testing headed behavior.
- Avoid randomizing every request; incoherent changes can look less realistic.
