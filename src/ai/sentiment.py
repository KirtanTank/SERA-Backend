def analyze_sentiment(text: str) -> str:
    text = text.lower()

    if any(word in text for word in ["sad", "tired", "upset"]):
        return "sad"
    if any(word in text for word in ["happy", "excited", "great"]):
        return "happy"

    return "neutral"
