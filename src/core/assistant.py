import json
from src.ai.sentiment import analyze_sentiment
from src.core.memory import ConversationMemory
from src.core.vector_memory import VectorMemory
from src.ai.llm import call_llm
from src.tools.executor import execute_tool
from src.core.profile import UserProfile
import re
from src.ai.llm import stream_llm

CONFIRMATION_REQUIRED_TOOLS = {"send_email", "create_calendar_event"}
CONFIRMATION_APPROVAL_ANSWERS = {
    "yes",
    "confirm",
    "go ahead",
    "proceed",
    "sure",
    "do it",
    "okay",
    "ok",
    "yup",
}
CONFIRMATION_REJECTED_ANSWERS = {
    "no",
    "cancel",
    "stop",
    "don't",
    "do not",
    "nope",
    "leave it",
    "nay",
}


class SERA:
    def __init__(self):
        self.memory = ConversationMemory()
        self.vector_memory = VectorMemory()
        self.profile = UserProfile()

    def respond(self, message: str, session_id: str, user_id: str) -> str:
        pending = self.memory.get_pending_action(session_id)
        user_profile = self.profile.get_profile(user_id)

        if pending:
            if message.lower() in CONFIRMATION_APPROVAL_ANSWERS:
                tool_name = pending["tool_call"]["name"]
                arguments = pending["tool_call"]["arguments"]

                tool_result = execute_tool(
                    type(
                        "ToolCall",
                        (),
                        {
                            "function": type(
                                "Func", (), {"name": tool_name, "arguments": arguments}
                            )
                        },
                    )
                )

                self.memory.clear_pending_action(session_id)
                return f"✅ Done. Result:\n{tool_result}"

            if message.lower() in CONFIRMATION_REJECTED_ANSWERS:
                self.memory.clear_pending_action(session_id)
                return "❌ Okay, I have cancelled that action."

        sentiment = analyze_sentiment(message)

        messages = self.memory.get_messages(session_id)
        summary = self.memory.get_summary(session_id) or ""

        context = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-6:]])

        profile_block = (
            f"User profile:\n{user_profile}" if user_profile else "User profile: none"
        )

        prompt = [
            {
                "role": "system",
                "content": (
                    "You are SERA, a Smart Emotional Reasoning Assistant.\n"
                    "Use tools when needed to answer accurately.\n"
                    "Be empathetic based on user sentiment."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Sentiment: {sentiment}\n"
                    f"Summary: {summary}\n"
                    f"Recent conversation:\n{context}\n\n"
                    f"User says: {message}"
                ),
            },
            {
                "role": "user",
                "content": (f"{profile_block}\n\n" f"User says: {message}"),
            },
        ]

        response = call_llm(prompt)

        msg = response.choices[0].message

        if msg.tool_calls:
            tool_call = msg.tool_calls[0]
            tool_name = tool_call.function.name

            arguments = json.loads(tool_call.function.arguments)

            # 🔒 Step 1: Check if confirmation needed
            if tool_name in CONFIRMATION_REQUIRED_TOOLS:
                self.memory.set_pending_action(
                    session_id,
                    {
                        "tool_call": {
                            "name": tool_name,
                            "arguments": tool_call.function.arguments,
                        }
                    },
                )

                return (
                    f"I'm about to **{tool_name.replace('_', ' ')}**.\n"
                    f"Do you want me to proceed? (yes / no)"
                )

            # ✅ Safe tools execute immediately
            tool_result = execute_tool({**arguments, "user_id": user_id})

            prompt.append(msg)
            prompt.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result),
                }
            )

            final_response = call_llm(prompt)
            reply = final_response.choices[0].message.content
            preferences = self.extract_preferences(message)
            for key, value in preferences.items():
                self.profile.set_preference(user_id, key, value)

        return reply

    def extract_preferences(self, message: str) -> dict:
        preferences = {}

        patterns = [
            (r"i like (.+)", "likes"),
            (r"i prefer (.+)", "preference"),
            (r"my timezone is (.+)", "timezone"),
            (r"i usually (.+)", "habit"),
        ]

        msg = message.lower()

        for pattern, key in patterns:
            match = re.search(pattern, msg)
            if match:
                preferences[key] = match.group(1)

        return preferences

    async def respond_stream(self, message: str, session_id: str, user_id: str):
        sentiment = analyze_sentiment(message)

        messages = self.memory.get_messages(session_id)
        summary = self.memory.get_summary(session_id) or ""
        profile = self.profile.get_profile(user_id)

        context = "\n".join(
            [f"{m['role']}: {m['content']}" for m in messages[-6:]]
        )

        prompt = [
            {
                "role": "system",
                "content": (
                    "You are SERA, a Smart Emotional Reasoning Assistant.\n"
                    "Respond clearly and empathetically.\n"
                    "Stream responses naturally."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Sentiment: {sentiment}\n"
                    f"Profile: {profile}\n"
                    f"Summary: {summary}\n"
                    f"Recent conversation:\n{context}\n\n"
                    f"User says: {message}"
                ),
            },
        ]

        full_reply = ""

        for token in stream_llm(prompt):
            full_reply += token
            yield token

        # 🔹 Save conversation AFTER streaming completes
        self.memory.add(session_id, "user", message)
        self.memory.add(session_id, "assistant", full_reply)

        # 🔹 Save structured preferences
        preferences = self.extract_preferences(message)
        for key, value in preferences.items():
            self.profile.set_preference(user_id, key, value)