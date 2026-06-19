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

## Context profile mode

Patchright defaults to the host browser's native locale, timezone, headers, and
media preferences. This is the strict anti-bot mode because fewer context
overrides means fewer behavioral mismatches.

Fingerprint-statistics pages such as AmiUnique also score how common each
browser-visible attribute is. For those cases, you can opt in to applying the
selected profile's context metadata while still avoiding viewport, user-agent,
and JavaScript fingerprint patches. This can align language, timezone, and media
metadata, but it does not make high-entropy fingerprints non-unique by itself:

```python
from webskrap import SessionConfig

config = SessionConfig(
    driver="patchright",
    channel="chrome",
    headless=True,
    mask_headless_user_agent=True,
    patchright_context_profile=True,
    reduce_fingerprint_surface=True,
    webrtc_ip_handling_policy="disable_non_proxied_udp",
)
```

This applies `locale`, `timezone_id`, `color_scheme`, `reduced_motion`, and any
caller-provided `extra_http_headers`. It keeps `no_viewport=True`, so screen and
window metrics still come from the browser or from `headless_screen`.

Set `webrtc_ip_handling_policy="disable_non_proxied_udp"` when leak-test pages
should not see local or direct public WebRTC ICE candidates. WebSkrap applies
Chromium's native process flags (`--webrtc-ip-handling-policy` plus
`--force-webrtc-ip-handling-policy`) instead of patching `RTCPeerConnection`.
The supported policy values are `default`,
`default_public_and_private_interfaces`, `default_public_interface_only`, and
`disable_non_proxied_udp`.

WebRTC IP handling only controls ICE candidates. It will not hide the page's
normal remote address, and it will not normalize unrelated fingerprint surfaces
such as fonts, canvas, battery, device memory, or TLS/session metadata.

Set `reduce_fingerprint_surface=True` to ask Chromium to disable WebGL and
canvas readback with native flags (`--disable-webgl` and
`--disable-reading-from-canvas`). This reduces rendering entropy on
fingerprint-statistics pages, but pages that require WebGL or canvas export may
not work correctly.

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

## Recipes

Headed Chrome for the strictest Patchright path:

```python
from pathlib import Path

from webskrap import SessionConfig

config = SessionConfig(
    driver="patchright",
    channel="chrome",
    headless=False,
    user_data_dir=Path(".webskrap/patchright-profile"),
)
```

Headless best-effort mode with a coherent virtual screen and browser-level
user-agent cleanup:

```python
from pathlib import Path

from webskrap import SessionConfig, Viewport

config = SessionConfig(
    driver="patchright",
    channel="chrome",
    headless=True,
    user_data_dir=Path(".webskrap/headless-profile"),
    headless_screen=Viewport(width=1366, height=768),
    mask_headless_user_agent=True,
)
```

Fingerprint-statistics and WebRTC leak-test mode:

```python
config = SessionConfig(
    driver="patchright",
    channel="chrome",
    headless=True,
    patchright_context_profile=True,
    reduce_fingerprint_surface=True,
    webrtc_ip_handling_policy="disable_non_proxied_udp",
)
```

Run the live test suite only when you intentionally want to hit third-party demo
sites:

```bash
WEBSKRAP_LIVE=1 pytest -q -m live
```
