from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional


class AnalyticsEvent:
    def __init__(self, event_name: str = "", data: Optional[Dict[str, Any]] = None):
        self.event_name = event_name
        self.data = data or {}