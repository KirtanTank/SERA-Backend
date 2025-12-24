from fastapi import APIRouter
from src.api.schemas import UserInput, SeraResponse
from src.core.assistant import SERA

router = APIRouter()
sera = SERA()

@router.post("/chat", response_model=SeraResponse)
def chat(payload: UserInput):
    reply = sera.respond(
        payload.message,
        payload.session_id,
        payload.user_id,
    )
    return {"response": reply}