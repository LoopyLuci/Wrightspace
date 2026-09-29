"""webbuilder.ml_engine.maxpool2d — 2D max pooling layer."""
from __future__ import annotations
from typing import Tuple
import numpy as np


class MaxPool2D:
    """2D max pooling layer."""

    def __init__(self, kernel_size: int = 2, stride: int = 2):
        if isinstance(kernel_size, int):
            kernel_size = (kernel_size, kernel_size)
        self.kernel_size = kernel_size
        self.stride = stride

    def forward(self, x: np.ndarray) -> np.ndarray:
        batch, channels, h, w = x.shape
        kh, kw = self.kernel_size
        out_h = (h - kh) // self.stride + 1
        out_w = (w - kw) // self.stride + 1
        out = np.zeros((batch, channels, out_h, out_w))
        for i in range(out_h):
            for j in range(out_w):
                region = x[:, :, i * self.stride:i * self.stride + kh,
                           j * self.stride:j * self.stride + kw]
                out[:, :, i, j] = np.max(region, axis=(2, 3))
        return out

    def backward(self, x: np.ndarray, grad_output: np.ndarray) -> np.ndarray:
        return grad_output

    def params(self) -> dict:
        return {}
