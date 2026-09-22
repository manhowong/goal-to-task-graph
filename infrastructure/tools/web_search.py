"""Web search adapter that exposes an MCP-backed search tool to workflow nodes."""

import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from infrastructure.config import PARALLEL_SEARCH_URL

WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Search the web for a current, real-world fact needed to decompose or "
            "judge a task — e.g. regulations, requirements, or availability."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "The search query."}},
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}


async def _search_web_async(query: str) -> str:
    async with streamable_http_client(PARALLEL_SEARCH_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("web_search", {"query": query})
            return "\n".join(block.text for block in result.content if hasattr(block, "text"))


def search_web(query: str) -> str:
    try:
        return asyncio.run(_search_web_async(query))
    except Exception as e:
        return f"Search failed: {e}"