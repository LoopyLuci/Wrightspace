"""webbuilder.gui.error_handler.get_error_logger — Factory for the error logger singleton."""

from __future__ import annotations
from typing import Optional

from webbuilder.gui.error_handler.errorlogger import ErrorLogger

_default_logger: Optional[ErrorLogger] = None


def get_error_logger() -> ErrorLogger:
    global _default_logger
    if _default_logger is None:
        _default_logger = ErrorLogger()
    return _default_logger


__all__ = ["get_error_logger"]