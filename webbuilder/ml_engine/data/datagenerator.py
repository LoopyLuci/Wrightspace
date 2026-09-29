"""webbuilder.ml_engine.data.datagenerator — Synthetic data generator for ML models."""
from __future__ import annotations
import numpy as np
from typing import Any, Dict, Tuple


class DataGenerator:
    """Generates synthetic training/validation data for ML models."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    @staticmethod
    def generate_color_data(n: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        rng = np.random.RandomState(42)
        colors = rng.randint(0, 256, size=(n, 33)).astype(np.float32)
        labels = rng.rand(n, 15).astype(np.float32)
        return colors, labels

    @staticmethod
    def generate_speed_data(n: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        rng = np.random.RandomState(42)
        features = rng.rand(n, 5).astype(np.float32) * 100
        labels = rng.rand(n, 2).astype(np.float32)
        return features, labels

    def generate_layout_data(self, n: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        rng = np.random.RandomState(self.seed)
        inputs = rng.rand(n, 20).astype(np.float32)
        targets = rng.randint(0, 5, size=(n,)).astype(np.int32)
        return inputs, targets

    def generate_typography_data(self, n: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        rng = np.random.RandomState(self.seed)
        features = rng.rand(n, 16).astype(np.float32) * 100
        labels = rng.randint(0, 8, size=(n,)).astype(np.int32)
        return features, labels

    def generate_all(self, n: int = 1000) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        return {
            "colors": self.generate_color_data(n),
            "speeds": self.generate_speed_data(n),
            "layouts": self.generate_layout_data(n),
            "typography": self.generate_typography_data(n),
        }
