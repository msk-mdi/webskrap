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
