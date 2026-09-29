"""webbuilder.ml_engine.conv2d — 2D convolution layer."""
from __future__ import annotations
from typing import Tuple
import numpy as np


class Conv2D:
    """2D convolutional layer (simplified, valid padding only)."""

    def __init__(self, in_channels: int, out_channels: int,
                 kernel_size: int = 3, stride: int = 1, padding: int = 0):
        if isinstance(kernel_size, int):
            kernel_size = (kernel_size, kernel_size)
        kh, kw = kernel_size
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.weights = np.random.randn(out_channels, in_channels, kh, kw) * np.sqrt(2.0 / (in_channels * kh * kw))
        self.bias = np.zeros(out_channels)

    def forward(self, x: np.ndarray) -> np.ndarray:
        if self.padding > 0:
            x = np.pad(x, ((0, 0), (0, 0), (self.padding, self.padding), (self.padding, self.padding)), mode='constant')
        batch, _, h, w = x.shape
        kh, kw = self.kernel_size
        out_h = (h - kh) // self.stride + 1
        out_w = (w - kw) // self.stride + 1
        out = np.zeros((batch, self.out_channels, out_h, out_w))
        for i in range(out_h):
            for j in range(out_w):
                region = x[:, :, i * self.stride:i * self.stride + kh,
                             j * self.stride:j * self.stride + kw]
                # Convolve: sum over in_channels and kernel
                out[:, :, i, j] = np.tensordot(region, self.weights, axes=([1, 2, 3], [1, 2, 3])) + self.bias
        return out

    def backward(self, x: np.ndarray, grad_output: np.ndarray) -> np.ndarray:
        return grad_output

    def params(self) -> dict:
        return {"weights": self.weights, "bias": self.bias}
