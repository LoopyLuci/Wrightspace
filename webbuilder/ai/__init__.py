"""webbuilder.ai.__init__ — AI integration (providers, caching, routing, chat sessions).

Supports 12 providers: OpenAI, Anthropic, Google Gemini, OpenRouter,
OpenCode Zen, OpenCode Go, Grok, Unsloth, LLM Studio, Nous, LM Studio,
and Ollama. Includes response caching, model routing, and chat session
management.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
import hashlib, json, os, time, uuid, copy, re, math
import numpy as np

# ══ Data classes ════════════════════════════════════════════════════════════

@dataclass
class ModelInfo:
    """Metadata for a single AI model."""
    id: str
    name: str
    provider: str = ""
    provider_name: str = ""
    context_window: int = 128000
    is_free: bool = False
    supports_streaming: bool = True
    supports_vision: bool = False
    supports_function_calling: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "provider": self.provider,
            "provider_name": self.provider_name, "context_window": self.context_window,
            "is_free": self.is_free, "supports_streaming": self.supports_streaming,
            "supports_vision": self.supports_vision, "supports_function_calling": self.supports_function_calling,
        }


@dataclass
class ChatMessage:
    """A single message in a chat session."""
    role: str = "user"
    content: str = ""
    sender: str = ""
    timestamp: str = ""
    model_used: str = ""

    def __post_init__(self):
        if not self.timestamp:
            from datetime import datetime as _dt
            self.timestamp = _dt.now().isoformat()


@dataclass
class ChatSession:
    """A chat session holding message history."""
    id: str = ""
    messages: list = field(default_factory=list)
    provider: str = "openai"
    model: str = "gpt-4o"
    system_prompt: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.created_at:
            from datetime import datetime as _dt
            now = _dt.now().isoformat()
            self.created_at = now
            self.updated_at = now

    def add_user_message(self, content: str) -> ChatMessage:
        msg = ChatMessage(role="user", content=content, sender="user")
        self.messages.append(msg)
        self.updated_at = msg.timestamp
        return msg

    def add_assistant_message(self, content: str, model_used: str = "") -> ChatMessage:
        msg = ChatMessage(role="assistant", content=content, sender="assistant", model_used=model_used or self.model)
        self.messages.append(msg)
        self.updated_at = msg.timestamp
        return msg

    def add_system_message(self, content: str) -> ChatMessage:
        msg = ChatMessage(role="system", content=content, sender="system")
        self.messages.insert(0, msg)
        return msg

    def get_last_user_message(self) -> str:
        for m in reversed(self.messages):
            if m.role == "user":
                return m.content
        return ""

    def clear(self):
        self.messages.clear()
        self.updated_at = time.strftime("%Y-%m-%dT%H:%M:%S")


# ══ Provider base class ══════════════════════════════════════════════════════

class BaseProvider:
    """Base class for all AI providers."""
    name: str = ""
    icon: str = ""
    type: str = "cloud"  # "cloud" or "local"
    endpoint: str = ""
    models: list = field(default_factory=list)

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self._models = list(self.models) if self.models else []

    def get_models(self) -> list:
        return list(self._models)

    def chat(self, model_id: str, messages: list, system_prompt: str = "",
             max_tokens: int = 1024, temperature: float = 0.7,
             stream_callback: Callable = None) -> dict:
        """Send a chat completion request. Returns {'content': str, 'model': str, 'usage': dict}."""
        raise NotImplementedError(f"{self.name}.chat() not implemented")

    def is_configured(self) -> bool:
        return bool(self.api_key)


# ══ Concrete provider implementations ═══════════════════════════════════════

class OpenAIProvider(BaseProvider):
    """OpenAI API provider (GPT-4, GPT-3.5, etc.)."""
    name = "OpenAI"
    icon = "🤖"
    type = "cloud"
    endpoint = "https://api.openai.com/v1/chat/completions"
    models = [
        {"id": "gpt-4o", "name": "GPT-4o", "context": 128000, "free": False},
        {"id": "gpt-4o-mini", "name": "GPT-4o-Mini", "context": 128000, "free": False},
        {"id": "gpt-4-turbo", "name": "GPT-4-Turbo", "context": 128000, "free": False},
        {"id": "gpt-4", "name": "GPT-4", "context": 8192, "free": False},
        {"id": "gpt-3.5-turbo", "name": "GPT-3.5-Turbo", "context": 16385, "free": False},
    ]

    def chat(self, model_id, messages, system_prompt="", max_tokens=1024, temperature=0.7, stream_callback=None):
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model_id, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
        if system_prompt:
            payload["messages"] = [{"role": "system", "content": system_prompt}] + messages
        response = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return {"content": content, "model": model_id, "usage": data.get("usage", {})}


class AnthropicProvider(BaseProvider):
    """Anthropic API provider (Claude 3.5, Claude 3 Opus, etc.)."""
    name = "Anthropic"
    icon = "🧠"
    type = "cloud"
    endpoint = "https://api.anthropic.com/v1/messages"
    models = [
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "context": 200000, "free": False},
        {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "context": 200000, "free": False},
        {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "context": 200000, "free": False},
        {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "context": 200000, "free": False},
        {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "context": 200000, "free": False},
    ]

    def chat(self, model_id, messages, system_prompt="", max_tokens=1024, temperature=0.7, stream_callback=None):
        import requests
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
        payload = {"model": model_id, "max_tokens": max_tokens, "temperature": temperature, "messages": messages}
        if system_prompt:
            payload["system"] = system_prompt
        response = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        content = data["content"][0]["text"]
        return {"content": content, "model": model_id, "usage": data.get("usage", {})}


class OpenRouterProvider(BaseProvider):
    """OpenRouter API provider (multi-model gateway)."""
    name = "OpenRouter"
    icon = "🔀"
    type = "cloud"
    endpoint = "https://openrouter.ai/api/v1/chat/completions"
    models = [
        {"id": "openrouter/auto", "name": "OpenRouter Auto", "context": 128000, "free": False},
        {"id": "openai/gpt-4o", "name": "GPT-4o via OpenRouter", "context": 128000, "free": False},
        {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet via OR", "context": 200000, "free": False},
        {"id": "google/gemini-2.0-flash", "name": "Gemini 2.0 Flash via OR", "context": 1000000, "free": False},
        {"id": "meta-llama/llama-3.1-405b", "name": "Llama 3.1 405B via OR", "context": 128000, "free": False},
    ]

    def chat(self, model_id, messages, system_prompt="", max_tokens=1024, temperature=0.7, stream_callback=None):
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json",
                   "HTTP-Referer": "https://webbuilder.app", "X-Title": "WebBuilder"}
        payload = {"model": model_id, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
        if system_prompt:
            payload["messages"] = [{"role": "system", "content": system_prompt}] + messages
        response = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return {"content": content, "model": model_id, "usage": data.get("usage", {})}


class OllamaProvider(BaseProvider):
    """Ollama local provider (Llama, Mistral, Gemma, etc.)."""
    name = "Ollama"
    icon = "🦙"
    type = "local"
    endpoint = "http://localhost:11434/api/chat"
    models = [
        {"id": "llama3.2", "name": "Llama 3.2", "context": 32768, "free": True},
        {"id": "llama3.1:70b", "name": "Llama 3.1 70B", "context": 131072, "free": True},
        {"id": "llama3.1:8b", "name": "Llama 3.1 8B", "context": 128000, "free": True},
        {"id": "mistral:7b", "name": "Mistral 7B", "context": 32768, "free": True},
        {"id": "gemma2:27b", "name": "Gemma 2 27B", "context": 8192, "free": True},
        {"id": "phi3.5:mini", "name": "Phi 3.5 Mini", "context": 128000, "free": True},
        {"id": "qwen2.5:7b", "name": "Qwen 2.5 7B", "context": 32768, "free": True},
        {"id": "deepseek-r1", "name": "DeepSeek-R1", "context": 128000, "free": True},
    ]

    def chat(self, model_id, messages, system_prompt="", max_tokens=1024, temperature=0.7, stream_callback=None):
        import requests
        payload = {"model": model_id, "messages": messages, "stream": False,
                   "options": {"num_predict": max_tokens, "temperature": temperature}}
        if system_prompt:
            payload["system"] = system_prompt
        response = requests.post(self.endpoint, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "")
        return {"content": content, "model": model_id, "usage": {}}


class OpenCodeGoProvider(BaseProvider):
    """OpenCode Go cloud provider."""
    name = "OpenCode Go"
    icon = "🐹"
    type = "cloud"
    endpoint = "https://api.opencode.ai/v1/chat/completions"
    models = [
        {"id": "opencode-go-default", "name": "OpenCode Go Default", "context": 128000, "free": False},
        {"id": "opencode-go-pro", "name": "OpenCode Go Pro", "context": 128000, "free": False},
    ]

    def chat(self, model_id, messages, system_prompt="", max_tokens=1024, temperature=0.7, stream_callback=None):
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model_id, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
        if system_prompt:
            payload["messages"] = [{"role": "system", "content": system_prompt}] + messages
        response = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return {"content": content, "model": model_id, "usage": data.get("usage", {})}


class OpenCodeZenProvider(BaseProvider):
    """OpenCode Zen cloud provider."""
    name = "OpenCode Zen"
    icon = "🧘"
    type = "cloud"
    endpoint = "https://api.opencode.ai/zen/v1/chat/completions"
    models = [
        {"id": "opencode-zen-default", "name": "OpenCode Zen Default", "context": 128000, "free": False},
    ]

    def chat(self, model_id, messages, system_prompt="", max_tokens=1024, temperature=0.7, stream_callback=None):
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model_id, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
        if system_prompt:
            payload["messages"] = [{"role": "system", "content": system_prompt}] + messages
        response = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return {"content": content, "model": model_id, "usage": data.get("usage", {})}


class GrokProvider(BaseProvider):
    """xAI Grok provider."""
    name = "xAI Grok"
    icon = "🐱"
    type = "cloud"
    endpoint = "https://api.x.ai/v1/chat/completions"
    models = [
        {"id": "grok-3", "name": "Grok-3", "context": 131072, "free": False},
        {"id": "grok-3-mini", "name": "Grok-3 Mini", "context": 131072, "free": False},
        {"id": "grok-2", "name": "Grok-2", "context": 131072, "free": False},
        {"id": "grok-2-mini", "name": "Grok-2 Mini", "context": 131072, "free": False},
    ]

    def chat(self, model_id, messages, system_prompt="", max_tokens=1024, temperature=0.7, stream_callback=None):
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model_id, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
        if system_prompt:
            payload["messages"] = [{"role": "system", "content": system_prompt}] + messages
        response = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return {"content": content, "model": model_id, "usage": data.get("usage", {})}


class NousProvider(BaseProvider):
    """Nous Research provider (local/cloud)."""
    name = "Nous"
    icon = "🧠"
    type = "local"
    endpoint = "http://localhost:11434/api/chat"
    models = [
        {"id": "nous-hermes3", "name": "Nous Hermes 3", "context": 8192, "free": True},
        {"id": "nous-capybara", "name": "Nous Capybara", "context": 4096, "free": True},
    ]

    def chat(self, model_id, messages, system_prompt="", max_tokens=1024, temperature=0.7, stream_callback=None):
        import requests
        payload = {"model": model_id, "messages": messages, "stream": False,
                   "options": {"num_predict": max_tokens, "temperature": temperature}}
        if system_prompt:
            payload["system"] = system_prompt
        response = requests.post(self.endpoint, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "")
        return {"content": content, "model": model_id, "usage": {}}


class LMStudioProvider(BaseProvider):
    """LM Studio local provider."""
    name = "LM Studio"
    icon = "🖥️"
    type = "local"
    endpoint = "http://localhost:1234/v1/chat/completions"
    models = [
        {"id": "lm-studio-default", "name": "LM Studio Default", "context": 128000, "free": True},
        {"id": "lm-studio-custom", "name": "LM Studio Custom Model", "context": 128000, "free": True},
    ]

    def chat(self, model_id, messages, system_prompt="", max_tokens=1024, temperature=0.7, stream_callback=None):
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model_id, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
        if system_prompt:
            payload["messages"] = [{"role": "system", "content": system_prompt}] + messages
        response = requests.post(self.endpoint, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return {"content": content, "model": model_id, "usage": data.get("usage", {})}


class UnslothProvider(BaseProvider):
    """Unsloth local provider (optimized models)."""
    name = "Unsloth"
    icon = "🧬"
    type = "local"
    endpoint = "http://localhost:11434/api/chat"
    models = [
        {"id": "unsloth-llama3.3:70b", "name": "Unsloth Llama 3.3 70B", "context": 128000, "free": True},
        {"id": "unsloth-llama3.1:8b", "name": "Unsloth Llama 3.1 8B", "context": 128000, "free": True},
        {"id": "unsloth-qwen2.5:7b", "name": "Unsloth Qwen 2.5 7B", "context": 32768, "free": True},
    ]

    def chat(self, model_id, messages, system_prompt="", max_tokens=1024, temperature=0.7, stream_callback=None):
        import requests
        payload = {"model": model_id, "messages": messages, "stream": False,
                   "options": {"num_predict": max_tokens, "temperature": temperature}}
        if system_prompt:
            payload["system"] = system_prompt
        response = requests.post(self.endpoint, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "")
        return {"content": content, "model": model_id, "usage": {}}


class LLMStudioProvider(BaseProvider):
    """LLM Studio local provider."""
    name = "LLM Studio"
    icon = "🏗️"
    type = "local"
    endpoint = "http://localhost:1234/v1/chat/completions"
    models = [
        {"id": "llm-studio-default", "name": "LLM Studio Default", "context": 128000, "free": True},
    ]

    def chat(self, model_id, messages, system_prompt="", max_tokens=1024, temperature=0.7, stream_callback=None):
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model_id, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
        if system_prompt:
            payload["messages"] = [{"role": "system", "content": system_prompt}] + messages
        response = requests.post(self.endpoint, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return {"content": content, "model": model_id, "usage": data.get("usage", {})}


class GoogleGeminiProvider(BaseProvider):
    """Google Gemini API provider."""
    name = "Google Gemini"
    icon = "🔮"
    type = "cloud"
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models"
    models = [
        {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "context": 1000000, "free": True},
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "context": 2000000, "free": False},
        {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "context": 1000000, "free": False},
        {"id": "gemini-2.0-flash-lite", "name": "Gemini 2.0 Flash-Lite", "context": 1000000, "free": True},
    ]

    def chat(self, model_id, messages, system_prompt="", max_tokens=1024, temperature=0.7, stream_callback=None):
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        url = f"{self.endpoint}/{model_id}:generateContent"
        payload = {"contents": messages, "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature}}
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]
        return {"content": content, "model": model_id, "usage": {}}


# ══ Model Router ═════════════════════════════════════════════════════════════

class ModelRouter:
    """Routes chat requests to configured providers. Singleton."""

    _instance: Optional["ModelRouter"] = None
    providers: dict = {}
    default_provider: str = "openai"
    default_model: str = "gpt-4o"

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._load_all_providers()

    @classmethod
    def get(cls) -> "ModelRouter":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def _load_all_providers(self):
        self.providers = {
            "openai": OpenAIProvider(""),
            "anthropic": AnthropicProvider(""),
            "google": GoogleGeminiProvider(""),
            "openrouter": OpenRouterProvider(""),
            "opencode_go": OpenCodeGoProvider(""),
            "opencode_zen": OpenCodeZenProvider(""),
            "grok": GrokProvider(""),
            "unsloth": UnslothProvider(""),
            "llm_studio": LLMStudioProvider(""),
            "lm_studio": LMStudioProvider(""),
            "nous": NousProvider(""),
            "ollama": OllamaProvider(""),
        }

    def get_provider(self, provider_id: str) -> BaseProvider:
        return self.providers.get(provider_id)

    def list_providers(self) -> list:
        return list(self.providers.keys())

    def list_models(self, provider_id: str = None) -> list:
        if provider_id:
            p = self.providers.get(provider_id)
            return p.get_models() if p else []
        result = {}
        for pid, p in self.providers.items():
            result[pid] = p.get_models()
        return result

    def route(self, provider_id: str, model_name: str, messages: list,
              system_prompt: str = "", max_tokens: int = 1024,
              temperature: float = 0.7) -> dict:
        provider = self.providers.get(provider_id)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_id}")
        return provider.chat(model_name, messages, system_prompt, max_tokens, temperature)

    def generate(self, prompt: str, provider_id: str = None, model_name: str = None,
                 system_prompt: str = "", max_tokens: int = 1024, temperature: float = 0.7) -> dict:
        provider_id = provider_id or self.default_provider
        model_name = model_name or self.default_model
        provider = self.providers.get(provider_id)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_id}")
        messages = [{"role": "user", "content": prompt}]
        return provider.chat(model_name, messages, system_prompt, max_tokens, temperature)

    def generate_from_session(self, session: ChatSession) -> dict:
        provider_id = session.provider or self.default_provider
        model_name = session.model or self.default_model
        provider = self.providers.get(provider_id)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_id}")
        messages = []
        if session.system_prompt:
            messages.append({"role": "system", "content": session.system_prompt})
        for msg in session.messages:
            messages.append({"role": msg.role, "content": msg.content})
        return provider.chat(model_name, messages, "", 1024, 0.7)

    def configure(self, provider_id: str, api_key: str):
        provider = self.providers.get(provider_id)
        if provider:
            provider.api_key = api_key

    def is_configured(self, provider_id: str) -> bool:
        provider = self.providers.get(provider_id)
        return provider.is_configured() if provider else False

    @property
    def all_providers(self) -> list:
        return [p.name for p in self.providers.values()]


def get_router() -> ModelRouter:
    """Get the singleton ModelRouter."""
    return ModelRouter.get()


def setup_providers(config: dict = None):
    """Configure providers from a config dict."""
    router = get_router()
    if config:
        for pid, key in config.items():
            router.configure(pid, key)


# ══ AI Client wrapper ═════════════════════════════════════════════════════════

class AIClient:
    """High-level AI client wrapping the ModelRouter with session support."""

    def __init__(self, provider_id: str = "openai", model: str = "gpt-4o"):
        self.provider_id = provider_id
        self.model = model
        self.router = get_router()
        self.session: Optional[ChatSession] = None

    def create_session(self, system_prompt: str = "") -> ChatSession:
        self.session = ChatSession(provider=self.provider_id, model=self.model, system_prompt=system_prompt)
        return self.session

    def chat(self, prompt: str, session: ChatSession = None) -> dict:
        session = session or self.session
        if not session:
            session = self.create_session()
        session.add_user_message(prompt)
        result = self.router.route(session.provider, session.model, session.messages, session.system_prompt)
        session.add_assistant_message(result["content"], result.get("model", session.model))
        return result

    def stream_chat(self, prompt: str, callback: Callable = None) -> str:
        raise NotImplementedError("Streaming not yet implemented for all providers")

    def get_available_models(self) -> list:
        return self.router.list_models(self.provider_id)

    def set_provider(self, provider_id: str, model: str = None):
        self.provider_id = provider_id
        if model:
            self.model = model

    def is_configured(self) -> bool:
        return self.router.is_configured(self.provider_id)


# ══ Response Cache ═══════════════════════════════════════════════════════════

class ResponseCache:
    """In-memory cache for AI responses."""

    _cache: dict = {}

    @classmethod
    def get(cls, key: str) -> Optional[dict]:
        return cls._cache.get(key)

    @classmethod
    def set(cls, key: str, value: dict):
        cls._cache[key] = value

    @classmethod
    def clear(cls):
        cls._cache.clear()

    @classmethod
    def make_key(cls, provider: str, model: str, prompt: str, system_prompt: str = "") -> str:
        h = hashlib.md5(f"{provider}:{model}:{system_prompt}:{prompt}".encode()).hexdigest()
        return h[:16]


# ══ Export symbols ═══════════════════════════════════════════════════════════

__all__ = [
    "ModelInfo", "ChatMessage", "ChatSession", "BaseProvider",
    "OpenAIProvider", "AnthropicProvider", "OpenRouterProvider",
    "GrokProvider", "NousProvider", "OllamaProvider", "LMStudioProvider",
    "GoogleGeminiProvider", "OpenCodeGoProvider", "OpenCodeZenProvider",
    "UnslothProvider", "LLMStudioProvider",
    "ModelRouter", "get_router", "setup_providers",
    "AIClient", "ResponseCache",
]
