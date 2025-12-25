import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api.routes import router as api_router
from src.api.websocket import router as ws_router
from src.jobs.scheduler import run_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # -------------------------
    # Startup
    # -------------------------
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    print("✅ Background scheduler started")

    yield

    # -------------------------
    # Shutdown
    # -------------------------
    print("🛑 SERA backend shutting down")


app = FastAPI(
    title="SERA Backend",
    lifespan=lifespan,
)

# -------------------------
# CORS (adjust origins later)
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Routers
# -------------------------
app.include_router(api_router, prefix="/api")
app.include_router(ws_router)


# -------------------------
# Health check
# -------------------------
@app.get("/")
async def health_check():
    return {"status": "SERA backend is running"}
