"""LLM client utilities used by workflow nodes for structured generation and tool use."""

import json
from openai import OpenAI
from infrastructure.config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME, MAX_TOKENS


def get_llm() -> OpenAI:
    """Instantiates and returns the OpenAI client configured via environment settings."""
    return OpenAI(
        base_url=OPENAI_BASE_URL,
        api_key=OPENAI_API_KEY,
    )


def run_llm(client: OpenAI, messages: list[dict], schema, max_tool_rounds: int = 1):
    """Executes chat completion with web search tool calls, forcing a structured parse output."""
    # Local import inside tool handler function to avoid circular imports
    from infrastructure.tools.web_search import WEB_SEARCH_TOOL, search_web

    for _ in range(max_tool_rounds):
        completion = client.chat.completions.parse(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=MAX_TOKENS,
            tools=[WEB_SEARCH_TOOL],
            response_format=schema,
            temperature=0,
        )
        message = completion.choices[0].message

        if not message.tool_calls:
            return message.parsed

        messages.append(message.model_dump(exclude_none=True))

        for call in message.tool_calls:
            query = json.loads(call.function.arguments)["query"]
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": search_web(query),
            })

    # Final attempt without tool offering to force a structured answer
    completion = client.chat.completions.parse(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=MAX_TOKENS,
        response_format=schema,
        temperature=0,
    )
    return completion.choices[0].message.parsed