from __future__ import annotations

import os

import pytest

from webskrap import ProxyConfig


def live_proxy() -> ProxyConfig | None:
    server = os.environ.get("WEBSKRAP_LIVE_PROXY")
    if not server:
        return None
    return ProxyConfig(
        server=server,
        username=os.environ.get("WEBSKRAP_LIVE_PROXY_USERNAME"),
        password=os.environ.get("WEBSKRAP_LIVE_PROXY_PASSWORD"),
    )


async def wait_for_recaptcha_score_or_skip(page) -> None:
    try:
        await page.wait_for_function(
            """() => /"score":\\s*\\d+\\.\\d+/.test(document.body.innerText)""",
            timeout=45_000,
        )
    except Exception as exc:  # noqa: BLE001 - patchright has its own TimeoutError type
        if exc.__class__.__name__ != "TimeoutError":
            raise
        text = await page.evaluate("() => document.body.innerText")
        if "grecaptcha.ready() fired" in text and "grecaptcha.execute" in text:
            pytest.skip("reCAPTCHA demo did not return a score after execute()")
        raise
