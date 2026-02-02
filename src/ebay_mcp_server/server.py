import logging

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger(__name__)

mcp = FastMCP("ebay")


def main():
    from ebay_mcp_server.tools import register_tools

    tool_count = register_tools(mcp)
    logger.info("Registered %d eBay tools", tool_count)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
