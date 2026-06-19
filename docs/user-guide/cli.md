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

The command prints status, final URL, title, and any artifact paths.

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

For fingerprint-statistics or WebRTC leak-test pages, apply profile
locale/timezone/media metadata and block non-proxied WebRTC UDP candidates
without viewport, user-agent, or JavaScript patches:

```bash
webskrap fetch https://amiunique.org/fr/fingerprint \
  --driver patchright \
  --channel chrome \
  --patchright-context-profile \
  --reduce-fingerprint-surface \
  --webrtc-ip-handling-policy disable_non_proxied_udp
```

Pass additional browser flags with repeated `--launch-arg=...` options. Use the
equals form when the browser flag itself starts with `--`.

## Screenshot

```bash
webskrap fetch https://example.com --screenshot example.png
```

## Save HTML

```bash
webskrap fetch https://example.com --output example.html
webskrap fetch https://example.com -o example.html --screenshot example.png
```

Parent directories are created automatically for `--output` and `--screenshot`.

## Wait and timeout

```bash
webskrap fetch https://example.com --wait-until load --timeout-ms 60000
```

Supported wait states are `commit`, `domcontentloaded`, `load`, and
`networkidle`. Prefer `domcontentloaded` for fast HTML collection, `load` for
regular page assets, and `networkidle` only when a page actually needs a quiet
network.

## Resource policy

```bash
webskrap fetch https://example.com --resource-policy lite
webskrap fetch https://example.com --resource-policy documents -o page.html
```

`lite` blocks images, fonts, and media. `documents` also blocks stylesheets.

## Options

```bash
webskrap fetch https://example.com \
  --driver playwright \
  --profile desktop-chrome \
  --channel chrome \
  --resource-policy lite \
  --patchright-context-profile \
  --reduce-fingerprint-surface \
  --webrtc-ip-handling-policy disable_non_proxied_udp \
  --timeout-ms 90000
```

## Launch arguments

Repeat `--launch-arg` for advanced browser flags:

```bash
webskrap fetch https://example.com \
  --headed \
  --launch-arg=--start-maximized \
  --launch-arg=--no-first-run
```

Use the equals form shown above so shell parsing keeps the browser flag attached
to the Typer option.
