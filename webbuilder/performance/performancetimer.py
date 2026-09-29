import time


class PerformanceTimer:
    def __init__(self, name, threshold_ms=1000):
        self.name = name
        self.threshold_ms = threshold_ms
        self.elapsed_ms: float = 0

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_ms = (time.perf_counter() - self._start) * 1000
        return False