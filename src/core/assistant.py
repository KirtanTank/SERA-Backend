from src.ai.sentiment import analyze_sentiment
class SERA:
    def __init__(self):
        self.memory = []

    def respond(self, message: str) -> str:
        sentiment = analyze_sentiment(message)

        reply = f"I sense a {sentiment} tone. You said: {message}"

        self.memory.append({
            "user": message,
            "sera": reply,
            "sentiment": sentiment
        })

        return reply
