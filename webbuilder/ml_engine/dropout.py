"""webbuilder.ml_engine.dropout — Dropout regularization layer."""
from __future__ import annotations
import numpy as np


class Dropout:
    """Inverted dropout layer."""

    def __init__(self, rate: float = 0.5):
        self.rate = rate
        self.training = True
        self._mask: np.ndarray = np.array([])

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        if training and self.rate > 0:
            self._mask = (np.random.rand(*x.shape) > self.rate) / (1 - self.rate)
            return x * self._mask
        return x

    def backward(self, x: np.ndarray, grad_output: np.ndarray) -> np.ndarray:
        if self.rate > 0:
            return grad_output * self._mask
        return grad_output

    def params(self) -> dict:
        return {}
