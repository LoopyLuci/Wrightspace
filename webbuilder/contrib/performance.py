import json
import time
import os
from pathlib import Path


class AutoSave:
    def __init__(self, save_func, interval=0):
        self._save_func = save_func
        self._interval = interval
        self._dirty = False

    def mark_dirty(self):
        self._dirty = True

    def check_and_save(self):
        if self._dirty:
            self._dirty = False
            self._save_func()

    def force_save(self):
        self._dirty = False
        self._save_func()


class CrashRecovery:
    def __init__(self, directory):
        self._directory = Path(directory)
        self._file = self._directory / "recovery.json"

    def save_session(self, data):
        payload = {"project": data}
        self._file.write_text(json.dumps(payload), encoding="utf-8")

    def has_recovery(self):
        return self._file.exists()

    def get_recovery(self):
        if self._file.exists():
            return json.loads(self._file.read_text(encoding="utf-8"))
        return None

    def clear_recovery(self):
        if self._file.exists():
            self._file.unlink()


class MemoryMonitor:
    def get_memory_usage(self):
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                "memory_mb": mem.used / (1024 * 1024),
                "warning": mem.percent > 70,
                "critical": mem.percent > 90,
            }
        except ImportError:
            return {
                "memory_mb": 0.0,
                "warning": False,
                "critical": False,
            }


class PerformanceTimer:
    def __init__(self, name, threshold_ms=1000):
        self.name = name
        self.threshold_ms = threshold_ms
        self.elapsed_ms = 0

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_ms = (time.perf_counter() - self._start) * 1000
        return False
