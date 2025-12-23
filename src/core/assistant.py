from src.ai.sentiment import analyze_sentiment
from src.core.memory import ConversationMemory
from src.core.vector_memory import VectorMemory

class SERA:
    def __init__(self):
        self.memory = ConversationMemory()
        self.vector_memory = VectorMemory()

    def respond(self, message: str, session_id: str) -> str:
        sentiment = analyze_sentiment(message)

        # Short-term memory
        history = self.memory.get(session_id)
        recent_context = " ".join(
            [m["content"] for m in history[-3:]]
        )

        # Long-term memory
        recalled = self.vector_memory.search(message)

        # Store important info
        if "remember" in message.lower():
            self.vector_memory.add(message)

        reply = (
            f"(Sentiment: {sentiment})\n"
            f"Recent context: {recent_context}\n"
            f"I recall: {recalled}\n"
            f"You said: {message}"
        )

        self.memory.add(session_id, "user", message)
        self.memory.add(session_id, "assistant", reply)

        return reply
