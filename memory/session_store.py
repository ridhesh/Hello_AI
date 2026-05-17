import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tools.bootstrap

import redis
import json
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class SessionStore:
    def __init__(self):
        self.memory = {} # Always initialize memory as a safety net
        try:
            self.redis = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=1)
            self.redis.ping()
            self.use_redis = True
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            logger.warning("⚠️ Redis unavailable. Using in-memory fallback for SessionStore.")
            self.use_redis = False

    def get(self, session_id: str) -> list:
        if self.use_redis:
            try:
                data = self.redis.get(session_id)
                if isinstance(data, (str, bytes, bytearray)):
                    return json.loads(data)
            except redis.exceptions.ConnectionError:
                logger.warning("⚠️ Redis connection lost. Switching to in-memory mode.")
                self.use_redis = False
        return self.memory.get(session_id, [])

    def set(self, session_id: str, history: list):
        if self.use_redis:
            try:
                self.redis.setex(session_id, 3600, json.dumps(history))
                return
            except redis.exceptions.ConnectionError:
                self.use_redis = False
        
        self.memory[session_id] = history
