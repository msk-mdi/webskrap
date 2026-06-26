from __future__ import annotations

from typing import cast, get_args

from webskrap.models import ResourcePolicy, WaitUntil, WebRtcIPHandlingPolicy


def parse_literal(value: str, literal: object, name: str) -> str:
    valid = get_args(literal)
    if value not in valid:
        raise ValueError(f"{name} must be one of: {', '.join(valid)}")
    return value


def parse_wait_until(value: str) -> WaitUntil:
    return cast(WaitUntil, parse_literal(value, WaitUntil, "wait_until"))


def parse_resource_policy(value: str) -> ResourcePolicy:
    try:
        return ResourcePolicy(value)
    except ValueError as exc:
        allowed = ", ".join(p.value for p in ResourcePolicy)
        raise ValueError(f"resource_policy must be one of: {allowed}") from exc


def parse_webrtc_ip_handling_policy(value: str | None) -> WebRtcIPHandlingPolicy | None:
    if value is None:
        return None
    return cast(
        WebRtcIPHandlingPolicy,
        parse_literal(value, WebRtcIPHandlingPolicy, "webrtc_ip_handling_policy"),
    )
