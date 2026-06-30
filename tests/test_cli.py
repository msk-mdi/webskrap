from __future__ import annotations

import json
from typing import Any

from typer.testing import CliRunner

from webskrap import cli
from webskrap.models import FetchResult

runner = CliRunner()


class _FakeClient:
    calls: list[dict[str, Any]] = []

    async def __aenter__(self) -> _FakeClient:
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    async def fetch(self, url: str, **kwargs: Any) -> FetchResult:
        self.calls.append({"url": url, **kwargs})
        text = "Readable body" if kwargs.get("text_only") else "<html>abcdef</html>"
        return FetchResult(
            url=url,
            final_url=f"{url}/final",
            status=200,
            ok=True,
            headers={"content-type": "text/html"},
            text=text,
            title="Example",
            cookies=[],
            timings={"elapsed_ms": 12.34},
        )


def _fake_client(monkeypatch: Any) -> None:
    _FakeClient.calls = []
    monkeypatch.setattr(cli, "WebSkrapClient", _FakeClient)


def test_fetch_json_is_bounded_and_uses_headless_stealth(monkeypatch: Any) -> None:
    _fake_client(monkeypatch)

    result = runner.invoke(
        cli.app,
        ["fetch", "https://example.test", "--format", "json", "--max-chars", "5"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload == {
        "url": "https://example.test",
        "final_url": "https://example.test/final",
        "status": 200,
        "ok": True,
        "title": "Example",
        "headers": {"content-type": "text/html"},
        "text": "<html",
        "text_length": 19,
        "text_truncated": True,
        "elapsed_ms": 12.3,
    }

    config = _FakeClient.calls[0]["config"]
    assert config.driver == "patchright"
    assert config.headless is True
    assert config.channel == "chrome"


def test_fetch_stdout_prints_raw_content(monkeypatch: Any) -> None:
    _fake_client(monkeypatch)

    result = runner.invoke(cli.app, ["fetch", "https://example.test", "--stdout"])

    assert result.exit_code == 0, result.output
    assert result.output == "<html>abcdef</html>"


def test_fetch_stdout_text_only_prints_readable_text(monkeypatch: Any) -> None:
    _fake_client(monkeypatch)

    result = runner.invoke(
        cli.app,
        ["fetch", "https://example.test", "--stdout", "--text-only"],
    )

    assert result.exit_code == 0, result.output
    assert result.output == "Readable body"
    assert _FakeClient.calls[0]["text_only"] is True


def test_fetch_quiet_suppresses_human_summary(monkeypatch: Any) -> None:
    _fake_client(monkeypatch)

    result = runner.invoke(cli.app, ["fetch", "https://example.test", "--quiet"])

    assert result.exit_code == 0, result.output
    assert result.output == ""


def test_profiles_json_is_parseable() -> None:
    result = runner.invoke(cli.app, ["profiles", "--format", "json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert [profile["name"] for profile in payload["profiles"]] == [
        "desktop-chrome",
        "desktop-edge",
        "mobile-chrome",
    ]


def test_doctor_json_success(monkeypatch: Any) -> None:
    async def fake_doctor() -> dict[str, object]:
        return {"ok": True, "message": "ready"}

    monkeypatch.setattr(cli, "_doctor", fake_doctor)

    result = runner.invoke(cli.app, ["doctor", "--format", "json"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == {"ok": True, "message": "ready"}


def test_doctor_json_failure(monkeypatch: Any) -> None:
    async def fake_doctor() -> dict[str, object]:
        return {"ok": False, "message": "broken", "hint": "fix it"}

    monkeypatch.setattr(cli, "_doctor", fake_doctor)

    result = runner.invoke(cli.app, ["doctor", "--format", "json"])

    assert result.exit_code == 1
    assert json.loads(result.output) == {"ok": False, "message": "broken", "hint": "fix it"}
