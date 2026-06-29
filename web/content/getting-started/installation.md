# Installation

Install WebSkrap from PyPI:

```bash
pip install webskrap
```

Install Playwright's Chromium browser:

```bash
python -m playwright install chromium
```

Verify the installation:

```bash
webskrap doctor
webskrap profiles
```

## Optional extras

Install only the extras you need:

```bash
pip install "webskrap[stealth]"      # Patchright driver
pip install "webskrap[mcp]"          # MCP stdio server
pip install "webskrap[mcp,stealth]"  # MCP plus stealth_fetch
```

Patchright uses its own browser install:

```bash
patchright install chromium
```

## Development install

For local development:

```bash
git clone https://github.com/kacigaya/webskrap.git
cd webskrap
pip install -e ".[dev,docs]"
python -m playwright install chromium
```

Run checks:

```bash
pytest -q
ruff check .
zensical build
```

If you use `uv`, the same checks can run through the project environment:

```bash
uv run pytest -q
uv run ruff check .
uv run zensical build
```
