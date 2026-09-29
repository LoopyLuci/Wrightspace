"""webbuilder.ai.router — Ai.Router.

Model routing and provider management for all 12 AI providers.
"""

from __future__ import annotations
from typing import Any, Callable, Optional, dict as DictType, list as ListType
from webbuilder.ai import (
    ModelInfo, ChatMessage, ChatSession, BaseProvider,
    OpenAIProvider, AnthropicProvider, OpenRouterProvider,
    GrokProvider, NousProvider, OllamaProvider, LMStudioProvider,
    GoogleGeminiProvider, OpenCodeGoProvider, OpenCodeZenProvider,
    UnslothProvider, LLMStudioProvider,
    get_router,
)


class Router:
    """Thin wrapper around ModelRouter for backward compatibility."""

    def __init__(self, config: Optional[DictType[str, str]] = None):
        self._router = get_router()
        if config:
            for pid, api_key in config.items():
                self._router.configure(pid, api_key)

    def generate(self, prompt: str, provider: str = "openai",
                 model: str = "gpt-4o", system: str = "",
                 max_tokens: int = 1024, temperature: float = 0.7) -> DictType[str, Any]:
        return self._router.generate(prompt, provider, model, system, max_tokens, temperature)

    def chat(self, messages: ListType[DictType[str, Any]], provider: str = "openai",
             model: str = "gpt-4o", system: str = "",
             max_tokens: int = 1024, temperature: float = 0.7) -> DictType[str, Any]:
        session = ChatSession(provider=provider, model=model, system_prompt=system)
        for m in messages:
            if m["role"] == "user":
                session.add_user_message(m["content"])
            elif m["role"] == "assistant":
                session.add_assistant_message(m["content"])
        return self._router.route(provider, model, session.messages, system, max_tokens, temperature)

    def list_providers(self) -> ListType[str]:
        return self._router.list_providers()

    def list_models(self, provider: Optional[str] = None) -> ListType[Any]:
        return self._router.list_models(provider)

    def configure(self, provider_id: str, api_key: str):
        self._router.configure(provider_id, api_key)

    def is_configured(self, provider_id: str) -> bool:
        return self._router.is_configured(provider_id)


def setup_providers(config: Optional[DictType[str, str]] = None):
    """Configure providers from a config dict."""
    router = get_router()
    if config:
        for pid, key in config.items():
            router.configure(pid, key)


def get_router_instance() -> Router:
    """Get a Router instance."""
    return Router()


__all__ = ["Router", "setup_providers", "get_router_instance", "ModelRouter", "ModelInfo"]
