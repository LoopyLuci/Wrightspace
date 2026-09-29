"""webbuilder.logging_config — Logging setup utilities."""
from __future__ import annotations
import logging
import sys
from pathlib import Path
from typing import Optional

_configured = False


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Configure logging for WebBuilder.
    
    Args:
        level: Logging level string (DEBUG, INFO, WARNING, etc.).
        log_file: Optional path to a log file.
    
    Returns:
        Configured root logger.
    """
    global _configured
    if _configured:
        return logging.getLogger("webbuilder")

    log_level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger("webbuilder")
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _configured = True
    return logger


def get_logger(name: str = "webbuilder") -> logging.Logger:
    """Get a logger for the given name."""
    return logging.getLogger(f"webbuilder.{name}")