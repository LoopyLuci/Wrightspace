"""webbuilder.ml_engine.persistence.delete_model — Delete a saved ML model."""

from __future__ import annotations
from pathlib import Path


def delete_model(model_path: str | Path) -> bool:
    """Delete a model file.

    Args:
        model_path: Path to the model file to delete.

    Returns:
        True if the file was deleted, False if it did not exist.
    """
    path = Path(model_path)
    if path.exists():
        path.unlink()
        return True
    return False


__all__ = ["delete_model"]
