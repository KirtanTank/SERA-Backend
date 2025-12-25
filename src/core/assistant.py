import json
import re
from typing import Dict

from src.ai.sentiment import analyze_sentiment
from src.ai.llm import call_llm, stream_llm
from src.core.memory import ConversationMemory
from src.core.profile import UserProfile
from src.core.vector_memory import VectorMemory
from src.tools.executor import execute_tool

CONFIRMATION_REQUIRED_TOOLS = {
    "send_email",
    "create_calendar_event",
    "create_reminder",
}

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
        self.profile = UserProfile()

    def respond(self, message: str, session_id: str, user_id: str) -> str:
        """
        Full reasoning + tool calling response
        """
        pending = self.memory.get_pending_action(session_id)
        if pending:
            return self._handle_confirmation(
                message=message,
                pending=pending,
                session_id=session_id,
                user_id=user_id,
            )

        sentiment = analyze_sentiment(message)
        messages = self.memory.get_messages(session_id)
        summary = self.memory.get_summary(session_id) or ""
        profile = self.profile.get_profile(user_id)

        context = "\n".join(f"{m['role']}: {m['content']}" for m in messages[-6:])

        vector_memory = VectorMemory(user_id)
        recalled_memory = vector_memory.search(message)

        prompt = [
            {
                "role": "system",
                "content": (
                    "You are SERA, a Smart Emotional Reasoning Assistant.\n"
                    "Be empathetic, precise, and use tools only when needed.\n"
                    "Do not invent user preferences."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Sentiment: {sentiment}\n"
                    f"User profile: {profile}\n"
                    f"Conversation summary: {summary}\n"
                    f"Recent conversation:\n{context}\n"
                    f"Relevant memories: {recalled_memory}\n\n"
                    f"User says: {message}"
                ),
            },
        ]

        response = call_llm(prompt)
        msg = response.choices[0].message

        if msg.tool_calls:
            tool_call = msg.tool_calls[0]
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if tool_name in CONFIRMATION_REQUIRED_TOOLS:
                self.memory.set_pending_action(
                    session_id,
                    {
                        "tool_call": {
                            "name": tool_name,
                            "arguments": arguments,
                        }
                    },
                )
                return (
                    f"I'm about to **{tool_name.replace('_', ' ')}**.\n"
                    f"Do you want me to proceed? (yes / no)"
                )
            tool_result = execute_tool(
                {
                    "name": tool_name,
                    **arguments,
                    "user_id": user_id,
                    "session_id": session_id,
                }
            )

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

        else:
            reply = msg.content

        self.memory.add(session_id, "user", message)
        self.memory.add(session_id, "assistant", reply)

        self._store_preferences(message, user_id)
        self._store_long_term_memory(message, vector_memory)

        return reply

    async def respond_stream(self, message: str, session_id: str, user_id: str):
        """
        Streaming response (no tools)
        """

        sentiment = analyze_sentiment(message)
        messages = self.memory.get_messages(session_id)
        summary = self.memory.get_summary(session_id) or ""
        profile = self.profile.get_profile(user_id)

        vector_memory = VectorMemory(user_id)
        recalled_memory = vector_memory.search(message)

        context = "\n".join(f"{m['role']}: {m['content']}" for m in messages[-6:])

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
                    f"User profile: {profile}\n"
                    f"Conversation summary: {summary}\n"
                    f"Recent conversation:\n{context}\n"
                    f"Relevant memories: {recalled_memory}\n\n"
                    f"User says: {message}"
                ),
            },
        ]

        full_reply = ""

        for token in stream_llm(prompt):
            full_reply += token
            yield token

        self.memory.add(session_id, "user", message)
        self.memory.add(session_id, "assistant", full_reply)

        self._store_preferences(message, user_id)
        self._store_long_term_memory(message, vector_memory)

    def _handle_confirmation(
        self,
        message: str,
        pending: Dict,
        session_id: str,
        user_id: str,
    ) -> str:
        msg = message.lower()

        if msg in CONFIRMATION_APPROVAL_ANSWERS:
            tool_name = pending["tool_call"]["name"]
            arguments = pending["tool_call"]["arguments"]

            tool_result = execute_tool(
                {
                    "name": tool_name,
                    **arguments,
                    "user_id": user_id,
                    "session_id": session_id,
                }
            )

            self.memory.clear_pending_action(session_id)
            return f"✅ Done.\n{tool_result}"

        if msg in CONFIRMATION_REJECTED_ANSWERS:
            self.memory.clear_pending_action(session_id)
            return "❌ Okay, I have cancelled that action."

        return "Please confirm with **yes** or **no**."

    def _store_preferences(self, message: str, user_id: str):
        preferences = self.extract_preferences(message)
        for key, value in preferences.items():
            self.profile.set_preference(user_id, key, value)

    def _store_long_term_memory(self, message: str, vector_memory: VectorMemory):
        keywords = ["remember", "i like", "i prefer", "my ", "always", "never"]
        if any(k in message.lower() for k in keywords):
            vector_memory.add(message)

    def extract_preferences(self, message: str) -> Dict:
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
