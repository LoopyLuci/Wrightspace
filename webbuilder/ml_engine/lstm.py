"""webbuilder.ml_engine.lstm — Long short-term memory layer (simplified)."""
from __future__ import annotations
import numpy as np


class LSTM:
    """Simplified single-layer LSTM."""

    def __init__(self, input_size: int, hidden_size: int):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.W_i = np.random.randn(input_size, hidden_size) * 0.01
        self.W_f = np.random.randn(input_size, hidden_size) * 0.01
        self.W_g = np.random.randn(input_size, hidden_size) * 0.01
        self.W_o = np.random.randn(input_size, hidden_size) * 0.01
        self.b_i = np.zeros(hidden_size)
        self.b_f = np.zeros(hidden_size)
        self.b_g = np.zeros(hidden_size)
        self.b_o = np.zeros(hidden_size)

    def forward(self, x: np.ndarray) -> np.ndarray:
        # x shape: (batch, seq_len, input_size) or (batch, input_size)
        if x.ndim == 2:
            x = x[:, None, :]
        batch, seq_len, _ = x.shape
        h = np.zeros((batch, self.hidden_size))
        c = np.zeros((batch, self.hidden_size))
        outputs = []
        for t in range(seq_len):
            x_t = x[:, t, :]
            i = self._sigmoid(x_t @ self.W_i + self.b_i)
            f = self._sigmoid(x_t @ self.W_f + self.b_f)
            g = np.tanh(x_t @ self.W_g + self.b_g)
            o = self._sigmoid(x_t @ self.W_o + self.b_o)
            c = f * c + i * g
            h = o * np.tanh(c)
            outputs.append(h)
        return np.stack(outputs, axis=1) if seq_len > 1 else h

    def backward(self, x: np.ndarray, grad_output: np.ndarray) -> np.ndarray:
        return grad_output

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    def params(self) -> dict:
        return {"W_i": self.W_i, "W_f": self.W_f, "W_g": self.W_g, "W_o": self.W_o,
                "b_i": self.b_i, "b_f": self.b_f, "b_g": self.b_g, "b_o": self.b_o}
