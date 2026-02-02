# Architecture

## Three-Layer Stack

```
ldraney-ebay-oauth (PyPI)        ← OAuth 2.0 token management
    ↓
ldraney-ebay-sdk (PyPI)          ← 8 eBay APIs, 188 endpoints
    ↓
ldraney-ebay-mcp-server (PyPI)   ← one MCP tool per SDK method  ← THIS REPO
```

Each layer is a separate PyPI package. Auth and SDK are complete. This repo is the top layer.

## SDK Structure (upstream, already published)

The SDK organizes 188 methods into 8 API classes under 3 domains:

```
EbayClient
├── buy_browse          → BuyBrowseApi        (7 methods)
├── sell_inventory      → SellInventoryApi     (30 methods)
├── sell_fulfillment    → SellFulfillmentApi   (14 methods)
├── sell_account        → SellAccountApi       (35 methods)
├── sell_finances       → SellFinancesApi      (8 methods)
├── sell_marketing      → SellMarketingApi     (63 methods)
├── sell_feed           → SellFeedApi          (22 methods)
└── commerce_taxonomy   → CommerceTaxonomyApi  (9 methods)
```

SDK methods follow consistent signatures:
- Path params are positional (`item_id: str`)
- Query params are keyword-only (`*, limit: int | None = None`)
- Request bodies are `body: dict[str, Any]`
- All return `Any` (JSON responses)

## MCP Server Structure (this repo)

```
src/ebay_mcp_server/
├── __init__.py
├── server.py              ← MCP server setup, calls register_tools()
└── tools/
    └── __init__.py        ← introspects all 8 SDK API classes, registers 188 tools
```

All tool registration is dynamic — `tools/__init__.py` iterates over every SDK API class, extracts method signatures via `inspect`, and registers each as an MCP tool at import time.

## Tool Naming Convention

`{api}_{method}` — e.g.:
- `buy_browse_search`
- `sell_inventory_create_or_replace_inventory_item`
- `commerce_taxonomy_get_category_suggestions`

## Parameter Mapping

| SDK signature | MCP tool input schema |
|---|---|
| `item_id: str` (positional) | `{"item_id": {"type": "string"}}` (required) |
| `*, limit: int \| None = None` | `{"limit": {"type": "integer"}}` (optional) |
| `body: dict[str, Any]` | `{"body": {"type": "object"}}` (required) |

## Auth Flow

1. User runs `ebay-oauth setup` (one-time, from `ldraney-ebay-oauth`)
2. Tokens stored in OS keychain
3. MCP server reads `EBAY_CLIENT_ID` / `EBAY_CLIENT_SECRET` from env
4. SDK handles token refresh automatically via `ldraney-ebay-oauth`
