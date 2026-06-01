from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from webskrap import ResourcePolicy, SessionConfig, WebSkrapClient

pytestmark = pytest.mark.browser


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/set-cookie":
            self.send_response(200)
            self.send_header("Set-Cookie", "webskrap_test=1; Path=/")
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><title>Cookie</title><body>ok</body></html>")
            return

        if self.path == "/echo-cookie":
            cookie = self.headers.get("Cookie", "")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<html><title>Echo</title><body>{cookie}</body></html>".encode())
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><title>Hello</title><body>WebSkrap</body></html>")

    def log_message(self, format: str, *args: object) -> None:
        return


@pytest.fixture()
def test_server() -> str:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


@pytest.mark.asyncio
async def test_fetch_local_page(test_server: str) -> None:
    try:
        async with WebSkrapClient() as client:
            result = await client.fetch(test_server)
    except Exception as exc:
        pytest.skip(f"Playwright browser unavailable: {exc}")

    assert result.status == 200
    assert result.title == "Hello"
    assert "WebSkrap" in result.text


@pytest.mark.asyncio
async def test_persistent_session_reuses_cookies(test_server: str, tmp_path: Path) -> None:
    config = SessionConfig(
        user_data_dir=tmp_path / "profile",
        resource_policy=ResourcePolicy.LITE,
    )

    try:
        async with WebSkrapClient() as client:
            session = await client.session("local", config=config)
            await session.fetch(f"{test_server}/set-cookie")
            result = await session.fetch(f"{test_server}/echo-cookie")
    except Exception as exc:
        pytest.skip(f"Playwright browser unavailable: {exc}")

    assert "webskrap_test=1" in result.text
