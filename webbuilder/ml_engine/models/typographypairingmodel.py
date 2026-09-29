"""webbuilder.ml_engine.models.typographypairingmodel — ML model."""
from __future__ import annotations
import numpy as np


class TypographyPairingModel:
    """typographypairingmodel model built with NumPy."""

    def __init__(self, **kwargs):
        self.input_size = kwargs.get("input_size", 10)
        self.output_size = kwargs.get("output_size", 1)

    def predict(self, colors, fonts, preferences=None) -> dict:
        return {
            "heading_font": "Inter",
            "body_font": "Roboto"
        }

    def fit(self, x: np.ndarray, y: np.ndarray, epochs: int = 10, lr: float = 0.001):
        pass

    def evaluate(self, x: np.ndarray, y: np.ndarray) -> float:
        preds = self.predict(x)
        return float(np.mean((preds - y) ** 2))
