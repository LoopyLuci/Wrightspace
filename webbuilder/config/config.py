"""webbuilder.config.config — Configuration manager."""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple


ProviderConfig = Dict[str, Any]


def _build_providers() -> Tuple[Dict[str, str], Dict[str, List[Dict[str, Any]]]]:
    providers: List[tuple[str, str, List[Dict[str, Any]]]] = [
        (
            "openai",
            "OpenAI",
            [
                {"id": "gpt-4o", "name": "GPT-4o", "context_window": 128000, "is_free": False},
                {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "context_window": 128000, "is_free": False},
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context_window": 16385, "is_free": False},
            ],
        ),
        (
            "anthropic",
            "Anthropic",
            [
                {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4", "context_window": 200000, "is_free": False},
                {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "context_window": 200000, "is_free": False},
            ],
        ),
        (
            "google",
            "Google",
            [
                {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "context_window": 1048576, "is_free": True},
            ],
        ),
        (
            "ollama",
            "Ollama (Local)",
            [
                {"id": "llama3.2", "name": "Llama 3.2", "context_window": 8192, "is_free": True, "local": True},
                {"id": "codellama", "name": "CodeLlama", "context_window": 16384, "is_free": True, "local": True},
            ],
        ),
        (
            "lmstudio",
            "LM Studio",
            [
                {"id": "local-model", "name": "Local Model", "context_window": 4096, "is_free": True, "local": True},
            ],
        ),
    ]
    names: Dict[str, str] = {}
    models: Dict[str, List[Dict[str, Any]]] = {}
    for provider_id, name, provider_models in providers:
        names[provider_id] = name
        models[provider_id] = provider_models
    return names, models


_PROVIDER_NAMES, _PROVIDER_MODELS = _build_providers()


class Config:
    _instance: Optional["Config"] = None

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self.providers: Dict[str, ProviderConfig] = {
            provider_id: {"name": _PROVIDER_NAMES[provider_id], "models": _PROVIDER_MODELS[provider_id]}
            for provider_id in _PROVIDER_NAMES
        }

    @classmethod
    def get(cls) -> "Config":
        return cls()

    def get_models_for_dropdown(self) -> List[Tuple[str, str, str, str, bool]]:
        models: List[Tuple[str, str, str, str, bool]] = []
        for provider_id, provider in self.providers.items():
            provider_name = str(provider.get("name", provider_id))
            for model in provider.get("models", []):
                is_free = bool(model.get("is_free", False))
                local = bool(model.get("local", False))
                source = provider_name
                models.append((
                    str(model.get("id", "")),
                    str(model.get("name", "")),
                    provider_id,
                    source,
                    is_free,
                ))
        models.sort(key=lambda m: (not m[4], m[2]))
        return models