# ebay-mcp-server

MCP server for creating eBay listings via Claude Desktop.

**Status:** In development. Auth layer complete, SDK and MCP tools in progress.

## What it does

Three tools that let Claude post to eBay:

1. **`ebay_search_categories`** — Find the right eBay category for an item
2. **`ebay_search_comps`** — Search active listings for pricing intelligence
3. **`ebay_create_listing`** — Create and publish a listing

## The workflow

```
You: [sends photo to Claude]
Claude: "Looks like a vintage desk lamp. I'd suggest..."
        - Title: Vintage Mid-Century Brass Desk Lamp
        - Category: Lamps (261713)
        - Condition: Used - Good
        - Price: $45 (based on similar listings at $35-60)
        - Description: [generated]
You: "Post it"
Claude: [calls ebay_create_listing] → "Listed! https://ebay.com/itm/..."
```

## Prerequisites

- Python 3.11+
- [ebay-oauth](https://github.com/ldraney/ebay-oauth) configured (`ebay-oauth setup`)
- eBay developer account with API keys

## Install

```bash
pip install ebay-mcp-server   # not yet published
# or
uvx ebay-mcp-server           # not yet published
```

## Development

```bash
git clone https://github.com/ldraney/ebay-mcp-server.git
cd ebay-mcp-server
poetry install
poetry run pytest tests/ -v
```

## Related

- [ebay-oauth](https://github.com/ldraney/ebay-oauth) — OAuth 2.0 token management (PyPI: `ldraney-ebay-oauth`)
