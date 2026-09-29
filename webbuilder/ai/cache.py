"""webbuilder.ai.cache — Response caching for AI provider calls.

Provides a TTL-based LRU cache to avoid redundant API calls.
Thread-safe via threading.RLock.
"""

from __future__ import annotations
import time
import threading
from collections import OrderedDict
from typing import Any


class ResponseCache:
    """Simple TTL-based response cache for AI completion results.

    Uses an OrderedDict for LRU eviction. Thread-safe via a reentrant lock.
    """

    def __init__(self, max_size: int = 256, ttl_seconds: int = 300):
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._store: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = threading.RLock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, ts = entry
            if time.time() - ts > self._ttl:
                del self._store[key]
                return None
            self._store.move_to_end(key)
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if key in self._store:
                del self._store[key]
            self._store[key] = (value, time.time())
            while len(self._store) > self._max_size:
                self._store.popitem(last=False)

    def invalidate(self, key: str) -> bool:
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def clear(self) -> int:
        with self._lock:
            n = len(self._store)
            self._store.clear()
            return n

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._store)
