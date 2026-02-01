# eBay MCP Server

## What This Is

An MCP server that lets Claude Desktop create eBay listings directly. Photo → Claude generates listing → user confirms → live on eBay. No browser, no copy-paste.

## Related Projects

- **[ebay-oauth](https://github.com/ldraney/ebay-oauth)** — OAuth 2.0 token lifecycle. Published on PyPI as `ldraney-ebay-oauth`. Already working: relay deployed to fly.io, sandbox tokens stored in OS keychain.
- **[ebay-mcp-server-old](https://github.com/ldraney/ebay-mcp-server-old)** — Archived first attempt. Has reference code for SDK wrappers and MCP tools but tests only mocked — no real API validation. Use as reference, not as a base.

## Development Philosophy

- **SDK first, MCP second.** Build thin Python wrappers around each eBay API. Validate every wrapper with pytest against the real sandbox. Only then wire up MCP tools.
- **Integration tests are the point.** Unit tests with mocks prove code structure. Integration tests against sandbox prove it works. Both matter, but integration tests gate progress.
- **Simplest thing that works.** Three MCP tools. Not a platform.
- **Validate by selling.** Done = item listed and sold on eBay, not code shipped.

## Architecture

```
Layer 1: ldraney-ebay-oauth (PyPI)   ← Auth — OAuth 2.0 token lifecycle  ✅ DONE
    ↓
Layer 2: ebay/ SDK wrappers          ← eBay API clients (Taxonomy, Browse, Inventory, Account)
    ↓
Layer 3: MCP tool layer              ← Three tools on top of the SDK
    ↓
Layer 4: .mcpb + PyPI                ← Distribution (uvx ebay-mcp-server)
```

## eBay APIs

| API | Purpose | Endpoint | Auth |
|-----|---------|----------|------|
| **Taxonomy** | Category suggestions, item aspects | `/commerce/taxonomy/v1` | Client Credentials |
| **Browse** | Search active listings for price comps | `/buy/browse/v1` | Client Credentials |
| **Inventory** | Create inventory items + offers | `/sell/inventory/v1` | User Token |
| **Account** | List fulfillment/payment/return policies | `/sell/account/v1` | User Token |

**Known limitation:** Sold items data requires the Marketplace Insights API, which needs special eBay developer approval. Browse API returns active listings only.

**Sandbox base:** `https://api.sandbox.ebay.com`
**Production base:** `https://api.ebay.com`

## Auth

Handled by `ldraney-ebay-oauth`. Credentials come from:
1. OS keychain (stored by `ebay-oauth setup`)
2. Environment variables as fallback

```
EBAY_CLIENT_ID=<your app id>
EBAY_CLIENT_SECRET=<your cert id>
EBAY_ENVIRONMENT=sandbox
```

See `~/secrets/ebay-sandbox.env` for actual values. Never commit credentials.

## MCP Tools

### 1. `ebay_search_categories`
Find eBay categories by keyword. Uses Taxonomy API `getCategorySuggestions`.

### 2. `ebay_search_comps`
Search active listings for pricing intelligence. Uses Browse API `search`.
(Renamed from `search_sold_comps` — it's active listings, not sold.)

### 3. `ebay_create_listing`
Create and publish a listing. Uses Inventory API: create item → create offer → publish.

Requires seller policies (fulfillment, payment, return) — use Account API to discover these.

## Build Order

1. **Auth** ✅ — `ebay-oauth` published, sandbox tokens working
2. **SDK: Taxonomy wrapper** — `get_category_suggestions()`, validated by pytest against sandbox
3. **SDK: Browse wrapper** — `search_active_listings()`, validated by pytest against sandbox
4. **SDK: Account wrapper** — `list_policies()`, needed before creating listings
5. **SDK: Inventory wrapper** — `create_item()`, `create_offer()`, `publish_offer()`, validated end-to-end
6. **MCP server** — Wire up SDK as three MCP tools
7. **First real listing** — Sandbox end-to-end smoke test
8. **Production** — Switch environment, list something real
9. **PyPI + mcpb** — `poetry publish`, build `.mcpb` for Claude Desktop

## Testing Strategy

```bash
# Unit tests (mocked, fast) — data transformation logic
poetry run pytest tests/unit/ -v

# Integration tests (real sandbox, slow) — actual eBay API calls
poetry run pytest tests/integration/ -v --run-integration

# All tests
poetry run pytest tests/ -v --run-integration
```

Integration tests require env vars set and hit the real eBay sandbox. Mark with `@pytest.mark.integration`.

## File Structure

```
ebay-mcp-server/
├── src/
│   └── ebay_mcp_server/
│       ├── __init__.py
│       ├── server.py              # MCP server entry point
│       ├── tools/
│       │   ├── search_categories.py
│       │   ├── search_comps.py
│       │   └── create_listing.py
│       └── ebay/
│           ├── client.py          # Async HTTP client using ebay-oauth
│           ├── taxonomy.py        # Taxonomy API wrapper
│           ├── browse.py          # Browse API wrapper
│           ├── inventory.py       # Inventory + Offer API wrapper
│           └── account.py         # Account API (policies)
├── tests/
│   ├── unit/
│   │   └── ebay/                  # Mocked unit tests
│   └── integration/
│       └── ebay/                  # Real sandbox API tests
├── pyproject.toml
├── CLAUDE.md
└── README.md
```

## Known Gotchas

- **Images**: eBay wants hosted URLs, not uploads. May need `ebay_upload_image` tool later.
- **Item Specifics**: Some categories require Brand, MPN, etc. Taxonomy API `getItemAspectsForCategory` discovers these.
- **Policies**: Offers require fulfillment/payment/return policy IDs. Must exist in seller account first.
- **Sandbox is flaky**: Some endpoints behave differently than production. Expect to debug on switch.
- **Rate limits**: Taxonomy API limited to 5,000 calls/day for Tier 1 apps.

## Definition of Done

Send Claude a photo, Claude generates listing data, you say "post it," it's live on eBay. No browser. No copy-paste.
