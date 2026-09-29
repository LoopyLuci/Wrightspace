"""webbuilder.ml_engine.denselayer — Dense (fully connected) layer."""
from __future__ import annotations
from typing import Tuple, Union
import numpy as np


class Dense:
    """Dense (fully connected) layer with optional activation."""

    def __init__(self, input_dim: int, output_dim: int, activation: str = "relu"):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.activation = activation
        self.weights = np.random.randn(input_dim, output_dim) * np.sqrt(2.0 / input_dim)
        self.bias = np.zeros(output_dim)
        self.params = {"W": self.weights, "b": self.bias}

    def forward(self, x: np.ndarray) -> np.ndarray:
        self._last_input = x
        z = x @ self.weights + self.bias
        if self.activation == "relu":
            return np.maximum(0, z)
        elif self.activation == "sigmoid":
            return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))
        elif self.activation == "tanh":
            return np.tanh(z)
        elif self.activation == "none" or self.activation is None:
            return z
        return z

    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        return grad_output @ self.weights.T
