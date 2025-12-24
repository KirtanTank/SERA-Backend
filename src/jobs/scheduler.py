import time
import json
from datetime import datetime
from src.jobs.reminders import redis_client

def run_scheduler():
    print("🔁 SERA background scheduler started")

    while True:
        now = datetime.utcnow().timestamp()

        jobs = redis_client.zrangebyscore(
            "sera:jobs", 0, now, start=0, num=5
        )

        for job_json in jobs:
            job = json.loads(job_json)

            handle_job(job)

            redis_client.zrem("sera:jobs", job_json)

        time.sleep(1)


def handle_job(job: dict):
    # For now, just log
    print(
        f"⏰ Reminder for user {job['user_id']}: {job['message']}"
    )

    # Later:
    # - Send WebSocket event
    # - Send email
