# Installation

Install WebSkrap from PyPI:

```bash
pip install webskrap
```

Download the browser binaries used by Playwright and Patchright:

```bash
webskrap install
```

Verify the installation:

```bash
webskrap doctor
webskrap profiles
```

## Included by default

`pip install webskrap` includes the Python dependencies for:

- Playwright browser automation.
- Patchright stealth sessions.
- The `webskrap-mcp` server.

The legacy extras `webskrap[stealth]` and `webskrap[mcp]` still install, but
they are no longer required.

Use machine-readable setup output in automation:

```bash
webskrap install --format json
webskrap doctor --format json
```

## Development install

For local development:

```bash
git clone https://github.com/kacigaya/webskrap.git
cd webskrap
pip install -e ".[dev]"
webskrap install
```

Run checks:

```bash
pytest -q
ruff check .
(cd web && bun run build)
```

If you use `uv`, the same checks can run through the project environment:

```bash
uv run pytest -q
uv run ruff check .
```
