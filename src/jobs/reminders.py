import redis
import json
import os
import uuid
from datetime import datetime

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

def schedule_reminder(user_id: str, session_id: str, message: str, run_at: str):
    job_id = str(uuid.uuid4())

    job = {
        "job_id": job_id,
        "user_id": user_id,
        "session_id": session_id,
        "type": "reminder",
        "message": message,
        "run_at": run_at,
    }

    redis_client.zadd(
        "sera:jobs",
        {json.dumps(job): datetime.fromisoformat(run_at).timestamp()}
    )

    return {"status": "scheduled", "job_id": job_id}
