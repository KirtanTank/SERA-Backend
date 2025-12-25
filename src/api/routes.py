from fastapi import APIRouter, HTTPException
from src.api.schemas import UserInput, SeraResponse
from src.core.assistant import SERA

router = APIRouter()
sera = SERA()


@router.post("/chat", response_model=SeraResponse)
async def chat(payload: UserInput):
    try:
        reply = sera.respond(
            payload.message,
            payload.session_id,
            payload.user_id,
        )
        return {"response": reply}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
