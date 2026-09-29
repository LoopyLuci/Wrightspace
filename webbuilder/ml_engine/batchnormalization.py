"""webbuilder.ml_engine.batchnormalization — Batch normalization layer."""
from __future__ import annotations
from typing import Any
import numpy as np


class BatchNorm:
    """Batch normalization layer for 2D input (batch_size, features)."""

    def __init__(self, num_features: int, eps: float = 1e-5, momentum: float = 0.1):
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum
        self.gamma = np.ones(num_features)
        self.beta = np.zeros(num_features)
        self.running_mean = np.zeros(num_features)
        self.running_var = np.ones(num_features)

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        if training:
            mean = x.mean(axis=0)
            var = x.var(axis=0)
            self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * mean
            self.running_var = (1 - self.momentum) * self.running_var + self.momentum * var
        else:
            mean = self.running_mean
            var = self.running_var
        x_norm = (x - mean) / np.sqrt(var + self.eps)
        return self.gamma * x_norm + self.beta

    def backward(self, x: np.ndarray, grad_output: np.ndarray) -> np.ndarray:
        return grad_output

    def params(self) -> dict:
        return {"gamma": self.gamma, "beta": self.beta}
