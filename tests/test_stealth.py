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
