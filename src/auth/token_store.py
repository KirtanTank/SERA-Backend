import redis
import json
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

def save_user_tokens(user_id: str, creds):
    redis_client.set(
        f"sera:oauth:{user_id}",
        json.dumps({
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        })
    )

def load_user_tokens(user_id: str):
    data = redis_client.get(f"sera:oauth:{user_id}")
    return json.loads(data) if data else None
