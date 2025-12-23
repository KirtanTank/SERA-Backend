from pydantic import BaseModel

class UserInput(BaseModel):
    message: str

class SeraResponse(BaseModel):
    response: str
