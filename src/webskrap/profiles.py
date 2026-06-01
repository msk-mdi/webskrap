from __future__ import annotations

from webskrap.models import BrowserProfile, Viewport

_PROFILES: dict[str, BrowserProfile] = {
    "desktop-chrome": BrowserProfile(
        name="desktop-chrome",
        viewport=Viewport(width=1365, height=768),
        screen=Viewport(width=1440, height=900),
        locale="en-US",
        timezone_id="Europe/Paris",
        device_scale_factor=1,
        navigator_languages=["en-US", "en"],
        hardware_concurrency=8,
        device_memory=8,
        webgl_vendor="Google Inc. (Intel)",
        webgl_renderer="ANGLE (Intel, Intel(R) Iris(TM) Plus Graphics, OpenGL 4.1)",
    ),
    "desktop-edge": BrowserProfile(
        name="desktop-edge",
        viewport=Viewport(width=1440, height=810),
        screen=Viewport(width=1536, height=864),
        locale="en-US",
        timezone_id="Europe/Paris",
        device_scale_factor=1,
        navigator_languages=["en-US", "en"],
        hardware_concurrency=8,
        device_memory=8,
        webgl_vendor="Google Inc. (NVIDIA)",
        webgl_renderer="ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)",
    ),
    "mobile-chrome": BrowserProfile(
        name="mobile-chrome",
        user_agent=(
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        ),
        viewport=Viewport(width=412, height=915),
        screen=Viewport(width=412, height=915),
        locale="en-US",
        timezone_id="Europe/Paris",
        device_scale_factor=2.625,
        is_mobile=True,
        has_touch=True,
        navigator_languages=["en-US", "en"],
        hardware_concurrency=8,
        device_memory=8,
        webgl_vendor="Google Inc. (Qualcomm)",
        webgl_renderer="ANGLE (Qualcomm, Adreno (TM) 730, OpenGL ES 3.2)",
    ),
}


def list_profiles() -> tuple[BrowserProfile, ...]:
    return tuple(_PROFILES.values())


def get_profile(name: str | BrowserProfile | None = None) -> BrowserProfile:
    if isinstance(name, BrowserProfile):
        return name
    key = name or "desktop-chrome"
    try:
        return _PROFILES[key].model_copy(deep=True)
    except KeyError as exc:
        available = ", ".join(sorted(_PROFILES))
        msg = f"unknown profile '{key}'. Available profiles: {available}"
        raise ValueError(msg) from exc
