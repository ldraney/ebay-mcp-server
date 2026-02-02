# ebay-mcp-server

MCP server exposing all 188 eBay REST API methods as tools. Built on [ldraney-ebay-sdk](https://pypi.org/project/ldraney-ebay-sdk/).

## Goal

Wrap every method in `ldraney-ebay-sdk` as an MCP tool — one tool per SDK method, across all 8 APIs. When every SDK method has a corresponding MCP tool, this repo is done.

## Architecture

```
eBay OpenAPI Specs → ldraney-ebay-sdk (PyPI) → ebay-mcp-server (this repo)
```

Each SDK method becomes an MCP tool. Auth is handled by `ldraney-ebay-oauth` (transitive dependency from the SDK).

## APIs Exposed

| API | Endpoints | Tools |
|-----|-----------|-------|
| Buy Browse | 7 | search, get_item, get_items_by_item_group, etc. |
| Sell Inventory | 30 | create_offer, publish_offer, bulk_update, etc. |
| Sell Fulfillment | 14 | get_order, get_orders, issue_refund, etc. |
| Sell Account | 35 | get_return_policy, create_payment_policy, etc. |
| Sell Finances | 8 | get_transaction, get_payout, etc. |
| Sell Marketing | 63 | create_campaign, get_ad, update_bid, etc. |
| Sell Feed | 22 | create_task, get_input_file, download_file, etc. |
| Commerce Taxonomy | 9 | get_category_tree, get_category_suggestions, etc. |

## Prerequisites

- Python 3.11+
- [ebay-oauth](https://github.com/ldraney/ebay-oauth) configured (`ebay-oauth setup`)
- eBay developer account with API keys

## Install

```bash
pip install ldraney-ebay-mcp-server
```

## Usage

```json
{
  "mcpServers": {
    "ebay": {
      "command": "ebay-mcp-server",
      "env": {
        "EBAY_CLIENT_ID": "your-client-id",
        "EBAY_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

## Development

```bash
git clone https://github.com/ldraney/ebay-mcp-server.git
cd ebay-mcp-server
poetry install
poetry run ebay-mcp-server
```

## Related

- [ebay-oauth](https://github.com/ldraney/ebay-oauth) — OAuth 2.0 token management (PyPI: `ldraney-ebay-oauth`)
- [ebay-sdk](https://github.com/ldraney/ebay-sdk) — Python SDK wrapping all eBay REST APIs (PyPI: `ldraney-ebay-sdk`)

## License

MIT
