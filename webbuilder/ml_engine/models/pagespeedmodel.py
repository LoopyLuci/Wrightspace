"""webbuilder.ml_engine.models.pagespeedmodel — ML model."""
from __future__ import annotations
import numpy as np


class PageSpeedModel:
    """pagespeedmodel model built with NumPy."""

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

    def analyze(self, ttfb: int, page_size: int, requests: int, dom_size: int, js_count: int) -> dict:
        load_time = ttfb + page_size // 1000 + requests * 50
        lighthouse = max(0, min(100, 100 - requests * 2 - js_count * 3))
        grade = "A" if lighthouse >= 90 else "B" if lighthouse >= 70 else "C" if lighthouse >= 50 else "D"
        return {
            "load_time_ms": load_time,
            "lighthouse_score": lighthouse,
            "performance_grade": grade
        }
