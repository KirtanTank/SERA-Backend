from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from src.auth.google_oauth import get_google_oauth_flow
from src.auth.token_store import save_user_tokens

router = APIRouter(prefix="/auth")

@router.get("/google/login")
def google_login():
    flow = get_google_oauth_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )
    return RedirectResponse(auth_url)

@router.get("/google/callback")
def google_callback(request: Request):
    flow = get_google_oauth_flow()
    flow.fetch_token(authorization_response=str(request.url))

    creds = flow.credentials

    # You will get user_id from frontend session / JWT later
    user_id = "demo_user"

    save_user_tokens(user_id, creds)

    return {"status": "Google account connected successfully"}
