import redis
import json
import os
from typing import Dict

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
PROFILE_TTL = 60 * 60 * 24 * 30  # 30 days


class UserProfile:
    def __init__(self):
        self.redis = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, decode_responses=True
        )

    def _key(self, user_id: str) -> str:
        return f"sera:profile:{user_id}"

    def get_profile(self, user_id: str) -> Dict:
        data = self.redis.get(self._key(user_id))
        return json.loads(data) if data else {}

    def set_preference(self, user_id: str, key: str, value):
        profile = self.get_profile(user_id)
        profile[key] = value.strip()
        self.redis.set(self._key(user_id), json.dumps(profile), ex=PROFILE_TTL)

    def delete_preference(self, user_id: str, key: str):
        profile = self.get_profile(user_id)
        if key in profile:
            del profile[key]
            self.redis.set(self._key(user_id), json.dumps(profile), ex=PROFILE_TTL)

    def clear_profile(self, user_id: str):
        self.redis.delete(self._key(user_id))
