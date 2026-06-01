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

## Development Install

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
mkdocs build --strict
```
