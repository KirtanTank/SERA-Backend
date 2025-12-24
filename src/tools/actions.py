from datetime import datetime

def get_current_time(_: dict):
    return {
        "time": datetime.now().strftime("%H:%M:%S")
    }

def get_weather(payload: dict):
    city = payload.get("city", "unknown")
    # Dummy for now (replace with real API later)
    return {
        "city": city,
        "weather": "Clear",
        "temperature": "28°C"
    }
