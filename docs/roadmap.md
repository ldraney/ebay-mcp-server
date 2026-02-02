# Roadmap

## Phase 1: Project Scaffolding
- [ ] `pyproject.toml` with Poetry, entry point, dependencies
- [ ] `src/ebay_mcp_server/` package structure
- [ ] Basic MCP server that starts and connects

## Phase 2: Tool Generation
- [ ] Tool registration pattern (one SDK method → one MCP tool)
- [ ] Parameter schema extraction from SDK type hints/signatures
- [ ] Implement tools for all 8 API modules:
  - [ ] `buy_browse` (7 tools)
  - [ ] `sell_inventory` (36 tools)
  - [ ] `sell_fulfillment` (15 tools)
  - [ ] `sell_account` (37 tools)
  - [ ] `sell_finances` (8 tools)
  - [ ] `sell_marketing` (82 tools)
  - [ ] `sell_feed` (26 tools)
  - [ ] `commerce_taxonomy` (9 tools)

## Phase 3: Validation
- [ ] Verify tool count matches SDK method count (220)
- [ ] Test with Claude Desktop configuration
- [ ] Smoke test key flows (search → get item → create listing)

## Phase 4: Publish
- [ ] Publish to PyPI as `ldraney-ebay-mcp-server`
- [ ] Verify `pip install ldraney-ebay-mcp-server` works end-to-end
