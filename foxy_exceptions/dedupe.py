import time
import hashlib
from typing import Dict

from foxy_exceptions.logger import logger


class ErrorDedupe:
    def __init__(self, ttl: int = 60):
        self.ttl = ttl
        self._store: Dict[str, float] = {}

    def _hash(self, text: str) -> str:
        return hashlib.sha1(text.encode()).hexdigest()

    def should_send(self, error_text: str) -> bool:
        key = self._hash(error_text)
        now = time.time()

        ts = self._store.get(key)
        if ts and now - ts < self.ttl:
            logger.debug("Duplicate error suppressed")
            return False

        self._store[key] = now
        return True
