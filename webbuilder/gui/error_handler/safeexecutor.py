"""webbuilder.gui.error_handler.safeexecutor — Safe execution wrapper."""

from __future__ import annotations
from typing import Any, Callable


class SafeExecutor:
    def __init__(self, error_logger: Any):
        self._error_logger = error_logger

    def execute(self, func: Callable, *, component: str = "", default: Any = None) -> Any:
        try:
            return func()
        except Exception as e:
            if self._error_logger:
                self._error_logger.log_error(component, e)
            return default


__all__ = ["SafeExecutor"]
