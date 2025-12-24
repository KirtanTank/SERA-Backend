from src.ai.llm import client

def summarize_conversation(
    previous_summary: str | None,
    messages: list[dict]
) -> str:
    conversation_text = "\n".join(
        [f"{m['role']}: {m['content']}" for m in messages]
    )

    prompt = f"""
You are summarizing a conversation for long-term memory.

Existing summary:
{previous_summary or "None"}

New conversation content:
{conversation_text}

Instructions:
- Keep it concise
- Preserve user preferences, emotions, goals
- Remove small talk
- Write in third person

Updated summary:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()
