from __future__ import annotations

from webskrap import BrowserProfile, StealthConfig
from webskrap.stealth import build_stealth_script


def test_stealth_script_contains_configured_profile_values() -> None:
    profile = BrowserProfile(
        name="test",
        navigator_languages=["en-US", "en"],
        hardware_concurrency=12,
        device_memory=16,
        webgl_vendor="Vendor",
        webgl_renderer="Renderer",
    )

    script = build_stealth_script(profile, StealthConfig())

    assert '"hardwareConcurrency":12' in script
    assert '"deviceMemory":16' in script
    assert '"webglVendor":"Vendor"' in script
    assert '"webglRenderer":"Renderer"' in script
    assert "Navigator.prototype" in script


def test_disabled_stealth_keeps_flags_in_script_payload() -> None:
    profile = BrowserProfile(name="test")
    script = build_stealth_script(profile, StealthConfig(patch_canvas=False))

    assert '"patchCanvas":false' in script


def test_headless_stealth_options_are_opt_in() -> None:
    profile = BrowserProfile(name="test")
    script = build_stealth_script(profile, StealthConfig())

    assert '"patchHeadlessUserAgent":false' in script
    assert '"patchWindowMetrics":false' in script


def test_headless_stealth_script_patches_user_agent_and_window_metrics() -> None:
    profile = BrowserProfile(name="test")
    script = build_stealth_script(
        profile,
        StealthConfig(patch_headless_user_agent=True, patch_window_metrics=True),
    )

    assert '"patchHeadlessUserAgent":true' in script
    assert '"patchWindowMetrics":true' in script
    assert "HeadlessChrome" in script
    assert "Navigator.prototype, \"userAgent\"" in script
    assert "outerWidth" in script
