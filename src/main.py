from fastapi import FastAPI
from src.api.routes import router
from src.api.websocket import router as ws_router

app = FastAPI(title="SERA Backend")

app.include_router(router)

app.include_router(ws_router)

@app.get("/")
def health_check():
    return {"status": "SERA backend is running"}
