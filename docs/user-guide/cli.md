# CLI

WebSkrap installs the `webskrap` command.

## Check Environment

```bash
webskrap doctor
```

## List Profiles

```bash
webskrap profiles
```

## Fetch A Page

```bash
webskrap fetch https://example.com
```

## Headed Browser

```bash
webskrap fetch https://example.com --headed
```

## Screenshot

```bash
webskrap fetch https://example.com --screenshot example.png
```

## Options

```bash
webskrap fetch https://example.com \
  --profile desktop-chrome \
  --channel chrome \
  --resource-policy lite \
  --timeout-ms 90000
```
