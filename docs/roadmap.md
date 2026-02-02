# Roadmap

## Phase 1: Project Scaffolding
- [x] `pyproject.toml` with Poetry, entry point, dependencies
- [x] `src/ebay_mcp_server/` package structure
- [x] Basic MCP server that starts and connects

## Phase 2: Tool Generation
- [x] Tool registration pattern (one SDK method → one MCP tool)
- [x] Parameter schema extraction from SDK type hints/signatures
- [x] All 8 API modules registered dynamically (188 tools total):
  - [x] `buy_browse` (7 tools)
  - [x] `sell_inventory` (30 tools)
  - [x] `sell_fulfillment` (14 tools)
  - [x] `sell_account` (35 tools)
  - [x] `sell_finances` (8 tools)
  - [x] `sell_marketing` (63 tools)
  - [x] `sell_feed` (22 tools)
  - [x] `commerce_taxonomy` (9 tools)

## Phase 3: Validation
- [ ] Verify tool count matches SDK method count (188)
- [ ] Test with Claude Desktop configuration
- [ ] Smoke test key flows (search → get item → create listing)

## Phase 4: Publish
- [ ] Publish to PyPI as `ldraney-ebay-mcp-server`
- [ ] Verify `pip install ldraney-ebay-mcp-server` works end-to-end
