"""webbuilder.ml_engine.persistence.load_model — Load a saved ML model."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, List, Union
import numpy as np


def load_model(path: str | Path, layers: Union[Any, List[Any], None] = None) -> Any:
    """Load a model from a JSON file and optionally restore weights into layers.

    Args:
        path: Path to the saved model file.
        layers: Optional layer or list of layers to restore weights into.

    Returns:
        The deserialized model data.

    Raises:
        FileNotFoundError: If the model file does not exist.
    """
    model_path = Path(path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {path}")
    with open(model_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    if layers is not None and isinstance(state, list):
        if not isinstance(layers, list):
            layers = [layers]
        for layer, layer_state in zip(layers, state):
            params = layer.params if not callable(getattr(layer, 'params', None)) else layer.params()
            for k, v in layer_state.get("params", {}).items():
                params[k] = np.array(v)

    return state


__all__ = ["load_model"]
