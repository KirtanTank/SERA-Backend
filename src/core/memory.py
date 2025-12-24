import redis
import json
import os
from typing import List, Dict, Optional

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

class ConversationMemory:
    def __init__(self):
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )

    def _conversation_key(self, session_id: str) -> str:
        return f"sera:conversation:{session_id}"

    def _summary_key(self, session_id: str) -> str:
        return f"sera:summary:{session_id}"

    def add(self, session_id: str, role: str, content: str):
        message = {"role": role, "content": content}
        self.redis.rpush(
            self._conversation_key(session_id),
            json.dumps(message)
        )
        self.redis.expire(self._conversation_key(session_id), 3600)

    def get_messages(self, session_id: str) -> List[Dict]:
        messages = self.redis.lrange(
            self._conversation_key(session_id), 0, -1
        )
        return [json.loads(m) for m in messages]

    def get_summary(self, session_id: str) -> Optional[str]:
        return self.redis.get(self._summary_key(session_id))

    def save_summary(self, session_id: str, summary: str):
        self.redis.set(self._summary_key(session_id), summary)
        self.redis.expire(self._summary_key(session_id), 3600)

    def trim_messages(self, session_id: str, keep_last: int):
        messages = self.redis.lrange(
            self._conversation_key(session_id), -keep_last, -1
        )
        self.redis.delete(self._conversation_key(session_id))
        for msg in messages:
            self.redis.rpush(self._conversation_key(session_id), msg)
