from __future__ import annotations

import pytest
from pydantic import ValidationError

from webskrap import (
    BrowserProfile,
    ProxyConfig,
    ResourcePolicy,
    SessionConfig,
    StealthConfig,
    Viewport,
)


def test_profile_generates_context_options() -> None:
    profile = BrowserProfile(
        name="test",
        viewport=Viewport(width=1280, height=720),
        locale="en-US",
        timezone_id="Europe/Paris",
        navigator_languages=["en-US", "en"],
    )

    options = profile.to_context_options()

    assert options["viewport"] == {"width": 1280, "height": 720}
    assert options["locale"] == "en-US"
    assert options["timezone_id"] == "Europe/Paris"
    assert options["extra_http_headers"]["Accept-Language"] == "en-US,en;q=0.9"


def test_session_config_maps_proxy_and_storage_state() -> None:
    profile = BrowserProfile(name="test")
    config = SessionConfig(
        proxy=ProxyConfig(server="http://localhost:8080", username="user", password="pass"),
        storage_state={"cookies": [], "origins": []},
        resource_policy=ResourcePolicy.LITE,
    )

    options = config.context_options(profile)

    assert options["proxy"] == {
        "server": "http://localhost:8080",
        "username": "user",
        "password": "pass",
    }
    assert options["storage_state"] == {"cookies": [], "origins": []}


def test_patchright_context_omits_profile_by_default() -> None:
    profile = BrowserProfile(
        name="test",
        user_agent="Custom/1.0",
        navigator_languages=["fr-FR", "fr"],
    )
    config = SessionConfig(driver="patchright", headless=True)

    options = config.context_options(profile)

    assert options["no_viewport"] is True
    assert "user_agent" not in options
    assert "extra_http_headers" not in options


def test_patchright_headless_user_agent_patch_adds_coherent_context_headers() -> None:
    profile = BrowserProfile(
        name="test",
        user_agent="Mozilla/5.0 Chrome/120.0.0.0 Safari/537.36",
        locale="fr-FR",
        navigator_languages=["fr-FR", "fr"],
    )
    config = SessionConfig(
        driver="patchright",
        headless=True,
        stealth=StealthConfig(patch_headless_user_agent=True),
    )

    options = config.context_options(profile)

    assert options["user_agent"] == "Mozilla/5.0 Chrome/120.0.0.0 Safari/537.36"
    assert options["extra_http_headers"]["Accept-Language"] == "fr-FR,fr;q=0.9"


def test_proxy_requires_supported_scheme() -> None:
    with pytest.raises(ValidationError):
        ProxyConfig(server="localhost:8080")


def test_viewport_dimensions_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        Viewport(width=0, height=720)
