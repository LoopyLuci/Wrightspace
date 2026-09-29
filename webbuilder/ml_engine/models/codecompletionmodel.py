"""webbuilder.ml_engine.models.codecompletionmodel — ML model."""
from __future__ import annotations
import numpy as np


class CodeCompletionModel:
    """codecompletionmodel model built with NumPy."""

    def __init__(self, **kwargs):
        self.input_size = kwargs.get("input_size", 10)
        self.output_size = kwargs.get("output_size", 1)

    def predict(self, x: np.ndarray) -> np.ndarray:
        if x.ndim == 1:
            x = x.reshape(1, -1)
        return np.zeros((x.shape[0], self.output_size))

    def fit(self, x: np.ndarray, y: np.ndarray, epochs: int = 10, lr: float = 0.001):
        pass

    def evaluate(self, x: np.ndarray, y: np.ndarray) -> float:
        preds = self.predict(x)
        return float(np.mean((preds - y) ** 2))

    def complete(self, code: str) -> list:
        return [code + "</div>", code + " />"]
