from datetime import datetime
from src.jobs.reminders import schedule_reminder

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

def create_reminder(payload: dict):
    return schedule_reminder(
        user_id=payload["user_id"],
        session_id=payload["session_id"],
        message=payload["message"],
        run_at=payload["run_at"],
    )