import redis
import json
import os
from typing import List, Dict

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

class ConversationMemory:
    def __init__(self):
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )

    def _key(self, session_id: str) -> str:
        return f"sera:conversation:{session_id}"

    def add(self, session_id: str, role: str, content: str):
        message = {"role": role, "content": content}
        self.redis.rpush(self._key(session_id), json.dumps(message))
        self.redis.expire(self._key(session_id), 3600)  # 1 hour

    def get(self, session_id: str) -> List[Dict]:
        messages = self.redis.lrange(self._key(session_id), 0, -1)
        return [json.loads(m) for m in messages]

    def clear(self, session_id: str):
        self.redis.delete(self._key(session_id))
