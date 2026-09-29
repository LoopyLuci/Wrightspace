"""webbuilder.gui.error_handler — Gui.Error Handler."""

from __future__ import annotations
import logging
from pathlib import Path


def get_error_logger(name: str = "webbuilder") -> logging.Logger:
    """Get error logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
    return logger


class ErrorLogger:
    """Logs errors to file."""
    def __init__(self, log_dir: Path | None = None):
        self.log_dir = log_dir or Path.home() / ".webbuilder" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._logger = get_error_logger("webbuilder.error")
    
    def log(self, error: Exception, context: str = "") -> None:
        msg = f"[{context}] {type(error).__name__}: {error}"
        self._logger.error(msg)
    
    def log_traceback(self, error: Exception, context: str = "") -> None:
        import traceback
        msg = f"[{context}] {type(error).__name__}: {error}\n{traceback.format_exc()}"
        self._logger.error(msg)


class SafeExecutor:
    """Safely executes code, catching and logging errors."""
    def __init__(self, logger: ErrorLogger | None = None):
        self.logger = logger or ErrorLogger()
    
    def execute(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.log(e, f"SafeExecutor.execute({getattr(func, '__name__', str(func))})")
            raise


def GlobalExceptionHook():
    """Install global exception hook."""
    import sys
    
    def hook(exctype, value, traceback):
        logger = get_error_logger("webbuilder.global")
        logger.critical("Uncaught exception", exc_info=(exctype, value, traceback))
    
    sys.excepthook = hook
