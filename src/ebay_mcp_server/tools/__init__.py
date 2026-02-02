"""Auto-register one MCP tool per SDK method."""

import inspect
import json
import logging
import os
import threading
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

_MISSING = object()

# Keys must match the attribute names on EbayClient (e.g. client.buy_browse)
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

_client: EbayClient | None = None
_client_lock = threading.Lock()

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
    """Return a cached EbayClient, creating one on first call."""
    global _client
    if _client is not None:
        return _client
    with _client_lock:
        if _client is not None:
            return _client
        try:
            client_id = os.environ["EBAY_CLIENT_ID"]
            client_secret = os.environ["EBAY_CLIENT_SECRET"]
        except KeyError as e:
            raise RuntimeError(
                f"Missing required environment variable {e}. "
                "Set EBAY_CLIENT_ID and EBAY_CLIENT_SECRET."
            ) from e
        oauth = EbayOAuthClient(
            client_id=client_id,
            client_secret=client_secret,
        )
        sandbox = os.environ.get("EBAY_SANDBOX", "false").lower() in ("1", "true", "yes")
        _client = EbayClient(oauth, sandbox=sandbox)
        return _client


def _make_tool_fn(api_attr: str, method_name: str, params: list[dict]):
    """Build a closure that calls the SDK method with the right args."""

    def tool_fn(**kwargs: Any) -> str:
        client = _get_client()
        api = getattr(client, api_attr)
        method = getattr(api, method_name)
        # Split kwargs into positional and keyword based on param metadata
        positional: list[tuple[int, Any]] = []
        keyword = {}
        for idx, p in enumerate(params):
            name = p["name"]
            val = kwargs.get(name, _MISSING)
            if val is _MISSING:
                if p["positional"] and not p["optional"]:
                    raise ValueError(
                        f"Missing required parameter '{name}'"
                    )
                continue
            # Parse JSON strings back to dicts/lists for object params
            if p["type"] == "object" and isinstance(val, str):
                try:
                    val = json.loads(val)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Parameter '{name}' must be valid JSON: {exc}"
                    ) from exc
            if p["positional"]:
                positional.append((idx, val))
            else:
                keyword[name] = val
        # Build positional arg list, filling gaps with None
        pos_args: list[Any] = []
        if positional:
            max_idx = positional[-1][0]
            pos_args = [None] * (max_idx + 1)
            for idx, val in positional:
                pos_args[idx] = val
        try:
            result = method(*pos_args, **keyword)
        except Exception as exc:
            logger.exception("Tool %s.%s failed", api_attr, method_name)
            return json.dumps({"error": type(exc).__name__, "message": str(exc)})
        return json.dumps(result, default=str)

    return tool_fn


def register_tools(mcp: FastMCP) -> int:
    """Register all SDK methods as MCP tools. Returns the tool count."""
    count = 0

    for api_attr, api_cls in API_MODULES.items():
        def _is_method(obj: object) -> bool:
            return inspect.isfunction(obj) or inspect.ismethod(obj)

        methods = [
            (name, m)
            for name, m in inspect.getmembers(api_cls, predicate=_is_method)
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
