import os
from openai import OpenAI
from src.ai.tools_schema import TOOLS_SCHEMA

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(messages):
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS_SCHEMA,
        tool_choice="auto",
        temperature=0.5,
    )
