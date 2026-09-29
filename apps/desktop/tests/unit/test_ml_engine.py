#!/usr/bin/env python3
"""Tests for WebBuilder ML Engine."""

import sys
import os
import tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


class TestMLLayers:
    """Test core neural network layers."""

    def test_dense_forward(self):
        from webbuilder.ml_engine import Dense
        layer = Dense(10, 5, activation='relu')
        x = np.random.randn(3, 10)
        out = layer.forward(x)
        assert out.shape == (3, 5)

    def test_dense_backward(self):
        from webbuilder.ml_engine import Dense
        layer = Dense(10, 5, activation='relu')
        x = np.random.randn(3, 10)
        layer.forward(x)
        grad = np.ones((3, 5))
        dx = layer.backward(grad)
        assert dx.shape == (3, 10)

    def test_dropout(self):
        from webbuilder.ml_engine import Dropout
        layer = Dropout(0.2)
        x = np.random.randn(3, 10)
        out = layer.forward(x)
        assert out.shape == x.shape

    def test_batchnorm(self):
        from webbuilder.ml_engine import BatchNorm
        layer = BatchNorm(10)
        x = np.random.randn(3, 10)
        out = layer.forward(x)
        assert out.shape == x.shape

    def test_conv2d(self):
        from webbuilder.ml_engine import Conv2D
        layer = Conv2D(3, 16, 3, padding=1)
        x = np.random.randn(2, 3, 32, 32)
        out = layer.forward(x)
        assert out.shape == (2, 16, 32, 32)

    def test_maxpool2d(self):
        from webbuilder.ml_engine import MaxPool2D
        layer = MaxPool2D(2)
        x = np.random.randn(2, 3, 32, 32)
        out = layer.forward(x)
        assert out.shape == (2, 3, 16, 16)

    def test_lstm(self):
        from webbuilder.ml_engine import LSTM
        layer = LSTM(20, 32)
        x = np.random.randn(2, 10, 20)
        out = layer.forward(x)
        assert out.shape == (2, 10, 32)


class TestMLModels:
    """Test ML model classes."""

    def test_color_harmony_model(self):
        from webbuilder.ml_engine.models import ColorHarmonyModel
        model = ColorHarmonyModel()
        palette = model.generate('#3b82f6', 'professional', 'tech')
        assert 'primary' in palette
        assert 'secondary' in palette
        assert 'accent' in palette

    def test_page_speed_model(self):
        from webbuilder.ml_engine.models import PageSpeedModel
        model = PageSpeedModel()
        result = model.analyze(1500, 250000, 25, 800, 5)
        assert 'load_time_ms' in result
        assert 'lighthouse_score' in result
        assert 'performance_grade' in result

    def test_layout_gen_model(self):
        from webbuilder.ml_engine.models import LayoutGenerationModel
        model = LayoutGenerationModel()
        layout = model.generate(5, 'desktop')
        assert 'grid_positions' in layout
        assert 'spacing' in layout

    def test_typo_pair_model(self):
        from webbuilder.ml_engine.models import TypographyPairingModel
        model = TypographyPairingModel()
        result = model.predict(
            np.random.randn(1, 15).astype(np.float32),
            np.random.randn(1, 10).astype(np.float32),
            np.random.randn(1, 20).astype(np.float32)
        )
        assert 'heading_font' in result
        assert 'body_font' in result

    def test_a11y_model(self):
        from webbuilder.ml_engine.models import AccessibilityComplianceModel
        model = AccessibilityComplianceModel()
        result = model.analyze({'contrast_ratio': 4.5, 'alt_text_coverage': 0.8})
        assert 'wcag_level' in result
        assert 'compliance_score' in result
        assert 'violations' in result

    def test_code_complete_model(self):
        from webbuilder.ml_engine.models import CodeCompletionModel
        model = CodeCompletionModel()
        result = model.complete('<div class="container">')
        assert isinstance(result, list)

    def test_user_intent_model(self):
        from webbuilder.ml_engine.models import UserIntentPredictionModel
        model = UserIntentPredictionModel()
        result = model.predict({})
        assert 'predicted_action' in result
        assert 'confidence' in result


class TestModelFactory:
    """Test MLModelFactory."""

    def test_get_model(self):
        from webbuilder.ml_engine.models import MLModelFactory
        model = MLModelFactory.get('color_harmony')
        assert model is not None

    def test_list_models(self):
        from webbuilder.ml_engine.models import MLModelFactory
        models = MLModelFactory.list_models()
        assert len(models) == 7

    def test_load_all(self):
        from webbuilder.ml_engine.models import MLModelFactory
        loaded = MLModelFactory.load_all()
        assert isinstance(loaded, list)


class TestPersistence:
    """Test model persistence."""

    def test_save_load(self):
        from webbuilder.ml_engine import Dense
        from webbuilder.ml_engine.persistence import save_model, load_model
        
        layers = [Dense(10, 5, activation='relu')]
        save_model('test_model', layers)
        
        # Modify weights
        layers[0].params['W'] = np.zeros_like(layers[0].params['W'])
        
        # Load should restore
        load_model('test_model', layers)
        assert not np.allclose(layers[0].params['W'], 0)

    def test_model_exists(self):
        from webbuilder.ml_engine.persistence import model_exists, delete_model
        assert model_exists('test_model')
        delete_model('test_model')
        assert not model_exists('test_model')


class TestDataGenerator:
    """Test data generation."""

    def test_color_data(self):
        from webbuilder.ml_engine.data import DataGenerator
        X, y = DataGenerator.generate_color_data(100)
        assert X.shape == (100, 33)
        assert y.shape == (100, 15)

    def test_speed_data(self):
        from webbuilder.ml_engine.data import DataGenerator
        X, y = DataGenerator.generate_speed_data(100)
        assert X.shape == (100, 5)
        assert y.shape == (100, 2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
