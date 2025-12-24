from src.ai.sentiment import analyze_sentiment
from src.core.memory import ConversationMemory
from src.core.vector_memory import VectorMemory
from src.ai.llm import generate_response
from src.ai.summarizer import summarize_conversation

MAX_MESSAGES = 6
SUMMARY_TRIGGER = 10

class SERA:
    def __init__(self):
        self.memory = ConversationMemory()
        self.vector_memory = VectorMemory()

    def respond(self, message: str, session_id: str) -> str:
        sentiment = analyze_sentiment(message)

        messages = self.memory.get_messages(session_id)
        summary = self.memory.get_summary(session_id)

        # 🔹 Summarize if needed
        if len(messages) >= SUMMARY_TRIGGER:
            new_summary = summarize_conversation(
                previous_summary=summary,
                messages=messages[:-MAX_MESSAGES]
            )

            self.memory.save_summary(session_id, new_summary)
            self.memory.trim_messages(session_id, MAX_MESSAGES)
            messages = self.memory.get_messages(session_id)
            summary = new_summary

        # 🔹 Build short-term memory
        short_memory = "\n".join(
            [f"{m['role']}: {m['content']}" for m in messages]
        )

        # 🔹 Long-term memory
        long_memory = self.vector_memory.search(message)

        reply = generate_response(
            user_message=message,
            sentiment=sentiment,
            short_memory=f"{summary or ''}\n{short_memory}",
            long_memory=long_memory,
        )

        if self._is_important(message):
            self.vector_memory.add(message)

        self.memory.add(session_id, "user", message)
        self.memory.add(session_id, "assistant", reply)

        return reply

    def _is_important(self, message: str) -> bool:
        keywords = ["remember", "i like", "i prefer", "my", "always", "never"]
        return any(k in message.lower() for k in keywords)
