"""webbuilder.ml_engine.persistence.save_model — Save model to disk."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, List, Union
import numpy as np


def save_model(path: str, model_or_list: Union[Any, List[Any]]) -> str:
    """Save a trained model or list of layers to disk as JSON."""
    model_path = Path(path)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(model_or_list, list):
        layers = model_or_list
    else:
        layers = [model_or_list]

    state = []
    for layer in layers:
        layer_state = {
            "class": layer.__class__.__name__,
            "module": layer.__class__.__module__,
            "params": {}
        }
        params = layer.params if not callable(getattr(layer, 'params', None)) else layer.params()
        for k, v in params.items():
            if isinstance(v, np.ndarray):
                layer_state["params"][k] = v.tolist()
            else:
                layer_state["params"][k] = v
        state.append(layer_state)

    with open(model_path, "w") as f:
        json.dump(state, f)
    return str(model_path)
