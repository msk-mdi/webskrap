# MCP server

WebSkrap ships an optional [Model Context Protocol](https://modelcontextprotocol.io)
server. MCP clients such as Claude Desktop and Claude Code can call it to drive
scraping directly. It runs over stdio and exposes three tools.

## Install

```bash
pip install "webskrap[mcp]"
python -m playwright install chromium
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

`stealth_fetch` uses the Patchright driver, so it also needs the `stealth` extra:

```bash
pip install "webskrap[mcp,stealth]"
patchright install chromium
```

It accepts the same controls as the [Stealth](stealth.md) guide, including
`channel`, `headless`, `patchright_context_profile`, `reduce_fingerprint_surface`,
`mask_headless_user_agent`, and `webrtc_ip_handling_policy`.
