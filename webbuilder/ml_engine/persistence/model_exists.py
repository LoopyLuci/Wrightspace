"""webbuilder.ml_engine.persistence.model_exists — Check if a model file exists."""

from __future__ import annotations
from pathlib import Path


def model_exists(model_path: str | Path) -> bool:
    """Check whether a model file exists on disk.

    Args:
        model_path: Path to the model file.

    Returns:
        True if the file exists, False otherwise.
    """
    return Path(model_path).exists()


__all__ = ["model_exists"]
