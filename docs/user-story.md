# User Story

## The Problem

eBay's REST APIs span 8 services and 220 endpoints. Using them requires reading OpenAPI specs, managing OAuth tokens, and writing HTTP requests by hand. Even with the SDK, you still need to write Python scripts.

## The Solution

With `ldraney-ebay-mcp-server`, an AI assistant (Claude, or any MCP client) can call any eBay API endpoint directly as a tool — no code required from the user.

## Example: List an Item for Sale

**Without MCP (manual):**
1. Read eBay Inventory API docs
2. Write Python script to authenticate
3. Call `create_or_replace_inventory_item` with correct JSON body
4. Call `create_offer` with pricing and policies
5. Call `publish_offer` to make it live
6. Debug auth errors, body format, missing fields

**With MCP (conversational):**
> "List my vintage camera for $150 with free shipping"

The AI assistant calls the right tools in sequence — `sell_inventory_create_or_replace_inventory_item`, `sell_inventory_create_offer`, `sell_inventory_publish_offer` — handling the JSON bodies and API sequencing.

## Example: Research Before Buying

> "Find completed listings for ThinkPad X1 Carbon Gen 11 and tell me the average sold price"

The assistant calls `buy_browse_search` with the right filters and summarizes the results.

## Example: Manage Active Orders

> "Show me all orders from the last week that haven't shipped yet"

The assistant calls `sell_fulfillment_get_orders` with date filters and shipping status.

## Who This Is For

- eBay sellers who want AI-assisted listing and order management
- Developers building eBay integrations who want to prototype via conversation
- Anyone who'd rather talk to an AI than read API docs
