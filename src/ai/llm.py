import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(
    user_message: str,
    sentiment: str,
    short_memory: str,
    long_memory: list[str]
) -> str:
    system_prompt = f"""
You are SERA (Smart Emotional Reasoning Assistant).

Personality:
- Calm
- Thoughtful
- Emotionally intelligent
- Clear reasoning
- Not verbose unless needed

Rules:
- Use emotional intelligence based on sentiment
- Use memory ONLY if relevant
- If memory is empty, do not hallucinate
- Be helpful and human-like
"""

    memory_block = ""
    if short_memory:
        memory_block += f"\nRecent conversation:\n{short_memory}\n"

    if long_memory:
        memory_block += f"\nRelevant long-term memories:\n- " + "\n- ".join(long_memory)

    user_prompt = f"""
User sentiment: {sentiment}

{memory_block}

User says:
{user_message}

Respond intelligently, empathetically, and with reasoning.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # fast + cheap + smart
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.6,
    )

    return response.choices[0].message.content.strip()
