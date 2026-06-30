# MCP server

WebSkrap ships an optional [Model Context Protocol](https://modelcontextprotocol.io)
server. MCP clients such as Claude Desktop and Claude Code can call it to drive
scraping directly. It runs over stdio and exposes three tools.

## Install

```bash
pip install webskrap
webskrap install
```

Run the server:

```bash
webskrap-mcp
```

You can also run it as a module:

```bash
python -m webskrap.mcp_server
```

## Tools

| Tool | Purpose |
| --- | --- |
| `fetch` | Fetch a URL with a standard Playwright browser. |
| `stealth_fetch` | Fetch a URL with the Patchright stealth driver. |
| `doctor` | Check that Playwright and Chromium can launch. |

Both fetch tools return `status`, `final_url`, `title`, `ok`, `headers`, and the
page HTML in `text` (capped by `max_chars`, with `text_length` and
`text_truncated` reporting the full size).

## Tool arguments

`fetch` accepts:

| Argument | Default | Notes |
| --- | --- | --- |
| `url` | required | URL to load. |
| `profile` | `desktop-chrome` | Bundled profile name. |
| `wait_until` | `domcontentloaded` | `commit`, `domcontentloaded`, `load`, or `networkidle`. |
| `resource_policy` | `all` | `all`, `lite`, or `documents`. |
| `timeout_ms` | `30000` | Navigation timeout. |
| `max_chars` | `20000` | Maximum returned HTML characters. |

Example arguments:

```json
{
  "url": "https://example.com",
  "profile": "desktop-chrome",
  "resource_policy": "lite",
  "wait_until": "load",
  "max_chars": 5000
}
```

`stealth_fetch` accepts the same URL/profile/timeout/output-size controls plus
Patchright options:

```json
{
  "url": "https://example.com",
  "channel": "chrome",
  "headless": false,
  "patchright_context_profile": false,
  "reduce_fingerprint_surface": false,
  "mask_headless_user_agent": false,
  "webrtc_ip_handling_policy": null
}
```

## Register with a client

### Claude Code

```bash
claude mcp add webskrap -- webskrap-mcp
```

### Claude Desktop

```json
{
  "mcpServers": {
    "webskrap": {
      "command": "webskrap-mcp"
    }
  }
}
```

### Codex

Add a server entry to `~/.codex/config.toml`:

```toml
[mcp_servers.webskrap]
command = "webskrap-mcp"
args = []
```

## Stealth

`stealth_fetch` uses the Patchright driver and accepts the same controls as the
[Stealth](/docs/user-guide/stealth) guide, including
`channel`, `headless`, `user_data_dir`, `patchright_context_profile`,
`reduce_fingerprint_surface`, `mask_headless_user_agent`, and
`webrtc_ip_handling_policy`.

For headless best-effort stealth from MCP, use real Chrome and opt in only to the
native browser controls you need:

```json
{
  "url": "https://example.com",
  "channel": "chrome",
  "headless": true,
  "user_data_dir": ".webskrap/headless-profile",
  "mask_headless_user_agent": true,
  "patchright_context_profile": true,
  "webrtc_ip_handling_policy": "disable_non_proxied_udp"
}
```

The MCP server does not solve CAPTCHA challenges, bypass login walls, bypass
credential checks, or circumvent access controls.
