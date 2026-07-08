---
title: LLM Web Scraping and MCP Server for AI Agents
description: Use WebSkrap as an MCP web scraping server for LLM agents that need clean page text from live browser sessions instead of raw HTML.
---

# LLM Web Scraping and MCP Server for AI Agents

WebSkrap includes an MCP server so AI agents can fetch live web pages with a browser-backed scraper and receive clean page text instead of raw HTML.

This is useful for coding agents, research agents, and automation workflows that need current page content but should avoid flooding the language model with scripts, styles, and markup noise.

## Start the MCP server

```bash
pip install webskrap
webskrap install
webskrap-mcp
```

The MCP server exposes tools such as `fetch`, `stealth_fetch`, and `doctor`.

## CLI output for agents

The CLI also returns bounded JSON that is easy for agents to parse:

```bash
webskrap fetch https://example.com --format json --max-chars 12000
```

The JSON includes `url`, `final_url`, `status`, `ok`, `title`, `headers`, `text`, `text_length`, `text_truncated`, and `elapsed_ms`.

## Why clean text matters

Raw HTML can be thousands of tokens of boilerplate. WebSkrap focuses on browser-backed fetching with output formats that are easier for LLMs and agents to consume.

## Related docs

- [MCP Server](/docs/user-guide/mcp)
- [CLI](/docs/user-guide/cli)
- [Stealth](/docs/user-guide/stealth)
- [API Reference](/docs/api-reference)
