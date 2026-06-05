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

Preview docs locally:

```bash
mkdocs serve
```

Build docs:

```bash
mkdocs build --strict
```

## Publishing docs

Docs are deployed by GitHub Actions from `main`.

Repository settings must use:

- Settings
- Pages
- Source: GitHub Actions
