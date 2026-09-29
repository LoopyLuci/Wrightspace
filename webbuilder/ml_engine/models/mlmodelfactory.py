"""webbuilder.ml_engine.models.mlmodelfactory — ML model."""
from __future__ import annotations
import numpy as np


class MLModelFactory:
    """mlmodelfactory model built with NumPy."""

    _registry = {
        "color_harmony": "webbuilder.ml_engine.models.colorharmonymodel.ColorHarmonyModel",
        "page_speed": "webbuilder.ml_engine.models.pagespeedmodel.PageSpeedModel",
        "layout_generation": "webbuilder.ml_engine.models.layoutgenerationmodel.LayoutGenerationModel",
        "typography_pairing": "webbuilder.ml_engine.models.typographypairingmodel.TypographyPairingModel",
        "accessibility_compliance": "webbuilder.ml_engine.models.accessibilitycompliancemodel.AccessibilityComplianceModel",
        "code_completion": "webbuilder.ml_engine.models.codecompletionmodel.CodeCompletionModel",
        "user_intent": "webbuilder.ml_engine.models.userintentpredictionmodel.UserIntentPredictionModel",
    }

    @classmethod
    def get(cls, name: str):
        path = cls._registry.get(name)
        if path is None:
            return None
        parts = path.rsplit(".", 1)
        module_path, class_name = parts
        import importlib
        mod = importlib.import_module(module_path)
        return getattr(mod, class_name)()

    @classmethod
    def list_models(cls) -> list:
        return list(cls._registry.keys())

    @classmethod
    def load_all(cls) -> list:
        return [cls.get(name) for name in cls._registry]
