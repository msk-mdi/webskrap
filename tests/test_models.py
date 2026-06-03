from __future__ import annotations

import pytest
from pydantic import ValidationError

from webskrap import (
    BrowserProfile,
    ProxyConfig,
    ResourcePolicy,
    SessionConfig,
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


def test_headless_chromium_gets_simulated_screen() -> None:
    config = SessionConfig(driver="patchright", channel="chrome", headless=True)

    args = config.launch_options()["args"]

    assert "--window-size=1920,1080" in args
    assert "--window-position=0,0" in args
    assert "--screen-info={1920x1080}" in args


def test_headless_screen_size_is_configurable() -> None:
    config = SessionConfig(
        headless=True, headless_screen=Viewport(width=1366, height=768)
    )

    args = config.launch_options()["args"]

    assert "--window-size=1366,768" in args
    assert "--screen-info={1366x768}" in args


def test_headless_screen_can_be_disabled() -> None:
    config = SessionConfig(headless=True, headless_screen=None)

    assert "args" not in config.launch_options()


def test_headed_mode_omits_simulated_screen() -> None:
    config = SessionConfig(driver="patchright", channel="chrome", headless=False)

    assert "args" not in config.launch_options()


def test_user_launch_args_override_simulated_screen() -> None:
    config = SessionConfig(headless=True, launch_args=["--window-size=800,600"])

    args = config.launch_options()["args"]

    assert "--window-size=800,600" in args
    assert "--window-size=1920,1080" not in args
    # untouched flags still applied
    assert "--screen-info={1920x1080}" in args


def test_non_chromium_headless_omits_simulated_screen() -> None:
    config = SessionConfig(browser="firefox", headless=True)

    assert "args" not in config.launch_options()


def test_mask_headless_user_agent_defaults_off() -> None:
    assert SessionConfig().mask_headless_user_agent is False
    assert SessionConfig(mask_headless_user_agent=True).mask_headless_user_agent is True


def test_proxy_requires_supported_scheme() -> None:
    with pytest.raises(ValidationError):
        ProxyConfig(server="localhost:8080")


def test_viewport_dimensions_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        Viewport(width=0, height=720)
