from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(title="SERA Backend")

app.include_router(router)

@app.get("/")
def health_check():
    return {"status": "SERA backend is running"}
