import json
from src.ai.sentiment import analyze_sentiment
from src.core.memory import ConversationMemory
from src.core.vector_memory import VectorMemory
from src.ai.llm import call_llm
from src.tools.executor import execute_tool
import src.tools  # registers tools

CONFIRMATION_REQUIRED_TOOLS = {"send_email", "create_calendar_event"}
CONFIRMATION_APPROVAL_ANSWERS = {"yes", "confirm", "go ahead", "proceed", "sure", "do it", "okay", "ok", "yup"}
CONFIRMATION_REJECTED_ANSWERS = {"no", "cancel", "stop", "don't", "do not", "nope", "leave it", "nay"}

class SERA:
    def __init__(self):
        self.memory = ConversationMemory()
        self.vector_memory = VectorMemory()

    def respond(self, message: str, session_id: str) -> str:
        pending = self.memory.get_pending_action(session_id)

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
            tool_result = execute_tool({
                **arguments,
                "user_id": user_id
            })

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
