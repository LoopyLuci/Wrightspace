"""webbuilder.ai.cache.responsecache — TTL-based LRU response cache."""
from __future__ import annotations
import hashlib
import json
import threading
import time
from collections import OrderedDict
from typing import Any, Optional


class ResponseCache:
    """Thread-safe LRU cache with TTL for AI responses."""

    def __init__(self, max_memory_entries: int = 200, max_size: int = 200, ttl: float = 3600.0):
        self._cache: OrderedDict[str, tuple] = OrderedDict()
        self._max_size = max_memory_entries if max_memory_entries else max_size
        self._ttl = ttl
        self._lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def _make_key(self, messages: Any, model: str = "") -> str:
        if isinstance(messages, list):
            raw = json.dumps(messages, sort_keys=True)
        else:
            raw = str(messages)
        raw = f"{raw}|{model}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, messages: Any, model: str = "") -> Optional[Any]:
        key = self._make_key(messages, model)
        with self._lock:
            if key in self._cache:
                data, timestamp, entry_ttl = self._cache[key]
                if time.time() - timestamp < entry_ttl:
                    self._cache.move_to_end(key)
                    self.hits += 1
                    return data
                else:
                    del self._cache[key]
            self.misses += 1
            return None

    def put(self, messages: Any, model: str, response: Any, cost_usd: float = 0.0, ttl: Optional[float] = None) -> None:
        key = self._make_key(messages, model)
        effective_ttl = ttl if ttl is not None else self._ttl
        with self._lock:
            self._cache[key] = (response, time.time(), effective_ttl)
            self._cache.move_to_end(key)
            while len(self._cache) > self._max_size:
                self._cache.popitem(last=False)

    def set(self, prompt: str, response: Any, model: str = "", temperature: float = 0.7) -> None:
        key = self._make_key(prompt, model)
        with self._lock:
            self._cache[key] = (response, time.time(), self._ttl)
            self._cache.move_to_end(key)
            while len(self._cache) > self._max_size:
                self._cache.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
        self.hits = 0
        self.misses = 0

    def stats(self) -> dict:
        with self._lock:
            return {"size": len(self._cache), "max_size": self._max_size,
                    "hits": self.hits, "misses": self.misses}

    def get_stats(self) -> dict:
        with self._lock:
            return {"memory_entries": len(self._cache), "max_size": self._max_size,
                    "hits": self.hits, "misses": self.misses}
