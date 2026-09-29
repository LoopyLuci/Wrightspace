"""webbuilder.gui.error_handler.errorlogger — Error logging utility."""

from __future__ import annotations
from dataclasses import dataclass
from collections import deque


@dataclass
class ErrorRecord:
    component: str
    error_type: str
    message: str


class ErrorLogger:
    def __init__(self, *, max_history: int = 100):
        self._errors: deque[ErrorRecord] = deque(maxlen=max_history)

    def log_error(self, component: str, error: Exception) -> ErrorRecord:
        record = ErrorRecord(
            component=component,
            error_type=type(error).__name__,
            message=str(error),
        )
        self._errors.append(record)
        return record
