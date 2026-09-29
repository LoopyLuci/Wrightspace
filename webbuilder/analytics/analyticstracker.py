from __future__ import annotations
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


class AnalyticsEvent:
    def __init__(self, event_name: str, data: Dict[str, Any]):
        self.event_name = event_name
        self.data = data


class AnalyticsTracker:
    def __init__(self, path: Path):
        self.path = path
        self.events: List[AnalyticsEvent] = []

    def track(self, event_name: str, data: Dict[str, Any]):
        event = AnalyticsEvent(event_name, data)
        self.events.append(event)

    def get_events(self, event_name: str) -> List[AnalyticsEvent]:
        return [e for e in self.events if e.event_name == event_name]

    def get_stats(self) -> Dict[str, Any]:
        counts = Counter(e.event_name for e in self.events)
        return {"event_counts": dict(counts)}

    def close(self):
        self.events.clear()
