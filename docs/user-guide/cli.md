# CLI

WebSkrap installs the `webskrap` command.

## Check environment

```bash
webskrap doctor
```

## List profiles

```bash
webskrap profiles
```

## Fetch a page

```bash
webskrap fetch https://example.com
```

## Headed browser

```bash
webskrap fetch https://example.com --headed
```

## Patchright driver

```bash
webskrap fetch https://example.com --driver patchright --channel chrome --headed
```

Use headed Patchright with real Chrome for the strict stealth path. Headless
Patchright is best-effort:

```bash
webskrap fetch https://example.com --driver patchright --channel chrome
```

## Screenshot

```bash
webskrap fetch https://example.com --screenshot example.png
```

## Options

```bash
webskrap fetch https://example.com \
  --driver playwright \
  --profile desktop-chrome \
  --channel chrome \
  --resource-policy lite \
  --timeout-ms 90000
```
