# ebay-mcp-server

## What This Is

MCP server that wraps every method in `ldraney-ebay-sdk` as an MCP tool. One tool per SDK method, 220 endpoints across 8 APIs.

## Architecture

```
ldraney-ebay-oauth (PyPI)  ← auth
    ↓
ldraney-ebay-sdk (PyPI)    ← all 8 eBay APIs, 220 endpoints  ✅ DONE
    ↓
ebay-mcp-server (this repo) ← one MCP tool per SDK method
```

No SDK wrappers in this repo. The SDK is published and complete. This repo just wires it up as MCP tools.

## Dependencies

- `ldraney-ebay-sdk` — the SDK (pulls in `ldraney-ebay-oauth` transitively)
- `mcp` — MCP server framework
- Python 3.11+

## Definition of Done

1. Every method in `ldraney-ebay-sdk` has a corresponding MCP tool.
2. Published to PyPI as `ldraney-ebay-mcp-server`.

## Commands

```bash
poetry install
poetry run ebay-mcp-server
```
