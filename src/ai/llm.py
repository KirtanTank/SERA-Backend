import os
from openai import OpenAI
from src.ai.tools_schema import TOOLS_SCHEMA

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_llm(messages):
    """
    Non-streaming LLM call.
    Supports tool calling.
    """
    try:
        return client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
            temperature=0.5,
            timeout=30,
        )
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}") from e


def stream_llm(messages):
    """
    Streaming LLM call.
    Text-only (no tools).
    """
    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
            temperature=0.5,
            timeout=30,
        )

        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            if hasattr(delta, "content") and delta.content:
                yield delta.content

    except OpenAIError as e:
        yield "\n⚠️ Sorry, I am having trouble responding right now.\n"
