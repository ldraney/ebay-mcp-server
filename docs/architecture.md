# Architecture

## Three-Layer Stack

```
ldraney-ebay-oauth (PyPI)        ← OAuth 2.0 token management
    ↓
ldraney-ebay-sdk (PyPI)          ← 8 eBay APIs, 220 endpoints
    ↓
ldraney-ebay-mcp-server (PyPI)   ← one MCP tool per SDK method  ← THIS REPO
```

Each layer is a separate PyPI package. Auth and SDK are complete. This repo is the top layer.

## SDK Structure (upstream, already published)

The SDK organizes 220 methods into 8 API classes under 3 domains:

```
EbayClient
├── buy_browse          → BuyBrowseApi        (7 methods)
├── sell_inventory      → SellInventoryApi     (36 methods)
├── sell_fulfillment    → SellFulfillmentApi   (15 methods)
├── sell_account        → SellAccountApi       (37 methods)
├── sell_finances       → SellFinancesApi      (8 methods)
├── sell_marketing      → SellMarketingApi     (82 methods)
├── sell_feed           → SellFeedApi          (26 methods)
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
├── server.py              ← MCP server setup, client init
└── tools/
    ├── __init__.py        ← registers all tool modules
    ├── buy_browse.py
    ├── sell_inventory.py
    ├── sell_fulfillment.py
    ├── sell_account.py
    ├── sell_finances.py
    ├── sell_marketing.py
    ├── sell_feed.py
    └── commerce_taxonomy.py
```

One tools file per SDK API class. Each file iterates over the corresponding API class methods and registers them as MCP tools.

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
