"""webbuilder.gui.error_handler.globalexceptionhook — Global exception hook installation."""

from __future__ import annotations
from typing import Any


class GlobalExceptionHook:
    def __init__(self, logger: Any = None) -> None:
        self._logger = logger
