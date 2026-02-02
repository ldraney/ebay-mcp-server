"""Auto-register one MCP tool per SDK method."""

import inspect
import json
import logging
import os
from typing import Any

from ebay_oauth import EbayOAuthClient
from ebay_sdk import EbayClient
from mcp.server.fastmcp import FastMCP

from ebay_sdk.buy.browse import BuyBrowseApi
from ebay_sdk.sell.inventory import SellInventoryApi
from ebay_sdk.sell.fulfillment import SellFulfillmentApi
from ebay_sdk.sell.account import SellAccountApi
from ebay_sdk.sell.finances import SellFinancesApi
from ebay_sdk.sell.marketing import SellMarketingApi
from ebay_sdk.sell.feed import SellFeedApi
from ebay_sdk.commerce.taxonomy import CommerceTaxonomyApi

logger = logging.getLogger(__name__)

API_MODULES = {
    "buy_browse": BuyBrowseApi,
    "sell_inventory": SellInventoryApi,
    "sell_fulfillment": SellFulfillmentApi,
    "sell_account": SellAccountApi,
    "sell_finances": SellFinancesApi,
    "sell_marketing": SellMarketingApi,
    "sell_feed": SellFeedApi,
    "commerce_taxonomy": CommerceTaxonomyApi,
}

# Map stringified annotations to JSON schema types
_TYPE_MAP = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
}


def _annotation_to_type(ann_str: str) -> str:
    """Convert a Python type annotation string to a JSON-friendly type hint."""
    base = ann_str.replace(" | None", "").strip()
    return _TYPE_MAP.get(base, "object")


def _get_client() -> EbayClient:
    """Create an EbayClient from environment variables."""
    try:
        client_id = os.environ["EBAY_CLIENT_ID"]
        client_secret = os.environ["EBAY_CLIENT_SECRET"]
    except KeyError as e:
        raise RuntimeError(
            f"Missing required environment variable {e}. "
            "Set EBAY_CLIENT_ID and EBAY_CLIENT_SECRET."
        ) from None
    oauth = EbayOAuthClient(
        client_id=client_id,
        client_secret=client_secret,
    )
    sandbox = os.environ.get("EBAY_SANDBOX", "false").lower() in ("1", "true", "yes")
    return EbayClient(oauth, sandbox=sandbox)


def _make_tool_fn(api_attr: str, method_name: str, params: list[dict]):
    """Build a closure that calls the SDK method with the right args."""

    def tool_fn(**kwargs: Any) -> str:
        with _get_client() as client:
            api = getattr(client, api_attr)
            method = getattr(api, method_name)
            # Split kwargs into positional and keyword based on param metadata
            positional = []
            keyword = {}
            for p in params:
                name = p["name"]
                val = kwargs.get(name)
                if val is None and name not in kwargs:
                    if p["positional"]:
                        if not p["optional"]:
                            raise ValueError(
                                f"Missing required parameter '{name}'"
                            )
                        positional.append(None)
                    continue
                # Parse JSON strings back to dicts/lists for object params
                if p["type"] == "object" and isinstance(val, str):
                    val = json.loads(val)
                if p["positional"]:
                    positional.append(val)
                else:
                    keyword[name] = val
            # Trim trailing None values from positional args
            while positional and positional[-1] is None:
                positional.pop()
            result = method(*positional, **keyword)
            return json.dumps(result, default=str)

    return tool_fn


def register_tools(mcp: FastMCP) -> int:
    """Register all SDK methods as MCP tools. Returns the tool count."""
    count = 0

    for api_attr, api_cls in API_MODULES.items():
        methods = [
            (name, m)
            for name, m in inspect.getmembers(api_cls, predicate=inspect.isfunction)
            if not name.startswith("_")
        ]

        for method_name, method in methods:
            sig = inspect.signature(method)
            doc = (method.__doc__ or "").strip()
            tool_name = f"{api_attr}_{method_name}"

            # Build parameter metadata
            params = []
            for pname, param in sig.parameters.items():
                if pname == "self":
                    continue
                ann_str = (
                    inspect.formatannotation(param.annotation)
                    if param.annotation != inspect.Parameter.empty
                    else "str"
                )
                optional = param.default is not inspect.Parameter.empty
                positional = param.kind != inspect.Parameter.KEYWORD_ONLY
                params.append(
                    {
                        "name": pname,
                        "annotation": ann_str,
                        "type": _annotation_to_type(ann_str),
                        "optional": optional,
                        "positional": positional,
                    }
                )

            # Build the function signature description for the tool
            param_desc = []
            for p in params:
                req = "optional" if p["optional"] else "required"
                param_desc.append(f"  {p['name']} ({p['type']}, {req})")
            full_desc = doc
            if param_desc:
                full_desc += "\n\nParameters:\n" + "\n".join(param_desc)

            # Create and register the tool function
            fn = _make_tool_fn(api_attr, method_name, params)
            fn.__name__ = tool_name
            fn.__doc__ = full_desc

            # Build parameter annotations for FastMCP schema generation
            annotations = {}
            for p in params:
                if p["type"] == "string":
                    annotations[p["name"]] = str if not p["optional"] else str | None
                elif p["type"] == "integer":
                    annotations[p["name"]] = int if not p["optional"] else int | None
                elif p["type"] == "number":
                    annotations[p["name"]] = float if not p["optional"] else float | None
                elif p["type"] == "boolean":
                    annotations[p["name"]] = bool if not p["optional"] else bool | None
                else:
                    # dicts, lists, etc. — accept as JSON string or object
                    annotations[p["name"]] = str if not p["optional"] else str | None

            fn.__annotations__ = annotations
            fn.__annotations__["return"] = str

            # Set defaults for optional params
            defaults = {}
            for p in params:
                if p["optional"]:
                    defaults[p["name"]] = None

            if defaults:
                fn.__kwdefaults__ = defaults

            mcp.tool(name=tool_name, description=full_desc)(fn)
            count += 1

    return count
