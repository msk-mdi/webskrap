# Development

Clone the repository:

```bash
git clone https://github.com/kacigaya/webskrap.git
cd webskrap
```

Install development dependencies:

```bash
pip install -e ".[dev,docs]"
python -m playwright install chromium
```

Run tests and lint:

```bash
pytest -q
ruff check .
```

Build docs:

```bash
zensical build
```

Use the opt-in live tests only when you need to verify third-party bot-detection
behavior:

```bash
WEBSKRAP_LIVE=1 pytest -q -m live
```

They require network access, Patchright, an installed browser, and public demo
sites that can change independently from WebSkrap.

## With uv

The repository includes `uv.lock`, so you can run the same commands through
`uv` without activating a shell environment:

```bash
uv run pytest -q
uv run ruff check .
uv run zensical build
```

## Publishing docs

Docs are deployed by GitHub Actions from `main`.

Repository settings must use:

- Settings
- Pages
- Source: GitHub Actions
