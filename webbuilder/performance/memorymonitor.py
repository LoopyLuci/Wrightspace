class MemoryMonitor:
    def __init__(self):
        self._usages = []

    def get_memory_usage(self):
        try:
            import psutil
            mem = psutil.virtual_memory()
            result = {
                "memory_mb": mem.used / (1024 * 1024),
                "warning": mem.percent > 70,
                "critical": mem.percent > 90,
            }
        except ImportError:
            result = {
                "memory_mb": 0.0,
                "warning": False,
                "critical": False,
            }
        self._usages.append(result["memory_mb"])
        return result

    def _calculate_trend(self):
        if len(self._usages) < 2:
            return "stable"
        diffs = [self._usages[i + 1] - self._usages[i] for i in range(len(self._usages) - 1)]
        avg_diff = sum(diffs) / len(diffs)
        if avg_diff > 1.0:
            return "increasing"
        elif avg_diff < -1.0:
            return "decreasing"
        return "stable"
