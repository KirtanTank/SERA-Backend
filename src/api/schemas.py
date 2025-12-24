from pydantic import BaseModel

class UserInput(BaseModel):
    message: str
    session_id: str
    user_id: str

class SeraResponse(BaseModel):
    response: str
