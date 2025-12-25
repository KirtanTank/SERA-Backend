from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from src.auth.token_store import load_user_tokens


def get_user_credentials(user_id: str):
    data = load_user_tokens(user_id)
    if not data:
        raise Exception("User not authenticated with Google")

    return Credentials(**data)


def list_events(payload: dict):
    user_id = payload["user_id"]
    creds = get_user_credentials(user_id)

    service = build("calendar", "v3", credentials=creds)

    events = (
        service.events()
        .list(
            calendarId="primary",
            maxResults=5,
            orderBy="startTime",
            singleEvents=True,
        )
        .execute()
    )

    return events.get("items", [])
