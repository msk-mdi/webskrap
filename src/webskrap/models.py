from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ResourcePolicy(StrEnum):
    ALL = "all"
    LITE = "lite"
    DOCUMENTS = "documents"


class Viewport(BaseModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)

    def to_playwright(self) -> dict[str, int]:
        return {"width": self.width, "height": self.height}


class ProxyConfig(BaseModel):
    server: str
    bypass: str | None = None
    username: str | None = None
    password: str | None = None

    @field_validator("server")
    @classmethod
    def validate_server(cls, value: str) -> str:
        allowed_prefixes = ("http://", "https://", "socks4://", "socks5://")
        if not value.startswith(allowed_prefixes):
            msg = "proxy server must start with http://, https://, socks4://, or socks5://"
            raise ValueError(msg)
        return value

    def to_playwright(self) -> dict[str, str]:
        payload = {"server": self.server}
        if self.bypass:
            payload["bypass"] = self.bypass
        if self.username:
            payload["username"] = self.username
        if self.password:
            payload["password"] = self.password
        return payload


class StealthConfig(BaseModel):
    enabled: bool = True
    patch_webdriver: bool = True
    patch_chrome_runtime: bool = True
    patch_permissions: bool = True
    patch_plugins: bool = True
    patch_webgl: bool = True
    patch_canvas: bool = True
    patch_hardware: bool = True


class BrowserProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    user_agent: str | None = None
    viewport: Viewport = Field(default_factory=lambda: Viewport(width=1365, height=768))
    screen: Viewport = Field(default_factory=lambda: Viewport(width=1440, height=900))
    locale: str = "en-US"
    timezone_id: str = "Europe/Paris"
    device_scale_factor: float = Field(default=1.0, gt=0)
    is_mobile: bool = False
    has_touch: bool = False
    color_scheme: Literal["dark", "light", "no-preference", "null"] = "light"
    reduced_motion: Literal["reduce", "no-preference", "null"] = "no-preference"
    extra_http_headers: dict[str, str] = Field(default_factory=dict)
    navigator_languages: list[str] = Field(default_factory=lambda: ["en-US", "en"])
    hardware_concurrency: int = Field(default=8, ge=1, le=64)
    device_memory: int = Field(default=8, ge=1, le=128)
    webgl_vendor: str = "Google Inc. (Intel)"
    webgl_renderer: str = "ANGLE (Intel, Intel(R) Iris(TM) Plus Graphics, OpenGL 4.1)"

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            msg = "profile name cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("locale", "timezone_id")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "value cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def ensure_language_consistency(self) -> BrowserProfile:
        if not self.navigator_languages:
            self.navigator_languages = [self.locale]
        if self.locale not in self.navigator_languages:
            self.navigator_languages.insert(0, self.locale)
        return self

    def accept_language(self) -> str:
        languages = self.navigator_languages or [self.locale]
        weighted = [languages[0]]
        weighted.extend(
            f"{language};q={max(0.1, 1 - index * 0.1):.1f}"
            for index, language in enumerate(languages[1:], start=1)
        )
        return ",".join(weighted)

    def headers(self) -> dict[str, str]:
        headers = {
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": self.accept_language(),
            "Upgrade-Insecure-Requests": "1",
        }
        headers.update(self.extra_http_headers)
        return headers

    def to_context_options(self) -> dict[str, Any]:
        options: dict[str, Any] = {
            "viewport": self.viewport.to_playwright(),
            "screen": self.screen.to_playwright(),
            "locale": self.locale,
            "timezone_id": self.timezone_id,
            "device_scale_factor": self.device_scale_factor,
            "is_mobile": self.is_mobile,
            "has_touch": self.has_touch,
            "color_scheme": self.color_scheme,
            "reduced_motion": self.reduced_motion,
            "extra_http_headers": self.headers(),
        }
        if self.user_agent:
            options["user_agent"] = self.user_agent
        return options


class SessionConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    driver: Literal["playwright", "patchright"] = "playwright"
    browser: Literal["chromium", "firefox", "webkit"] = "chromium"
    channel: str | None = None
    headless: bool = True
    user_data_dir: Path | None = None
    storage_state: Path | dict[str, Any] | None = None
    proxy: ProxyConfig | None = None
    resource_policy: ResourcePolicy = ResourcePolicy.ALL
    stealth: StealthConfig = Field(default_factory=StealthConfig)
    ignore_https_errors: bool = False
    java_script_enabled: bool = True
    service_workers: Literal["allow", "block"] = "allow"
    timeout_ms: float = Field(default=30_000, gt=0)
    navigation_timeout_ms: float = Field(default=30_000, gt=0)
    default_timeout_ms: float = Field(default=30_000, gt=0)
    slow_mo_ms: float | None = Field(default=None, ge=0)
    launch_args: list[str] = Field(default_factory=list)

    def launch_options(self) -> dict[str, Any]:
        options: dict[str, Any] = {
            "headless": self.headless,
            "timeout": self.timeout_ms,
        }
        if self.channel:
            options["channel"] = self.channel
        if self.slow_mo_ms is not None:
            options["slow_mo"] = self.slow_mo_ms
        if self.launch_args:
            options["args"] = self.launch_args
        return options

    def context_options(self, profile: BrowserProfile) -> dict[str, Any]:
        if self.driver == "patchright":
            # patchright defeats CDP-aware detectors by presenting the browser's
            # real fingerprint. Injecting a synthetic viewport, locale, timezone,
            # or Accept-Language header reintroduces behavioral bot signals, so we
            # let the real environment show through instead of the profile.
            options: dict[str, Any] = {"no_viewport": True}
        else:
            options = profile.to_context_options()
        options.update(
            {
                "ignore_https_errors": self.ignore_https_errors,
                "java_script_enabled": self.java_script_enabled,
                "service_workers": self.service_workers,
            }
        )
        if self.proxy:
            options["proxy"] = self.proxy.to_playwright()
        if self.storage_state is not None and self.user_data_dir is None:
            options["storage_state"] = self.storage_state
        return options


class FetchResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    url: str
    final_url: str
    status: int | None
    ok: bool
    headers: dict[str, str]
    text: str
    title: str
    cookies: list[dict[str, Any]]
    timings: dict[str, float]
    screenshot_path: Path | None = None
