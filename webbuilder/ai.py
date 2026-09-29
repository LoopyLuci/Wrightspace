"""webbuilder.ai — AI module with provider routing and chat sessions."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import os


@dataclass
class ChatMessage:
    """A chat message."""
    role: str
    content: str


@dataclass
class ChatSession:
    """A chat session."""
    system_prompt: str
    messages: list[ChatMessage] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.messages:
            self.messages = [ChatMessage(role="system", content=self.system_prompt)]
    
    def add_user_message(self, content: str) -> ChatMessage:
        """Add a user message."""
        msg = ChatMessage(role="user", content=content)
        self.messages.append(msg)
        return msg
    
    def add_assistant_message(self, content: str) -> ChatMessage:
        """Add an assistant message."""
        msg = ChatMessage(role="assistant", content=content)
        self.messages.append(msg)
        return msg


@dataclass
class ModelInfo:
    """Model information."""
    provider_id: str
    model_id: str
    name: str
    context_window: int = 4096
    is_free: bool = False
    supports_streaming: bool = True
    
    def __str__(self) -> str:
        return self.name


class ModelRouter:
    """Routes model requests to appropriate providers."""
    
    def __init__(self, config=None):
        self.config = config
    
    def get_provider_for_model(self, model_name: str) -> str:
        """Get the provider ID for a given model name."""
        model_lower = model_name.lower()
        
        # OpenAI models
        if any(m in model_lower for m in ["gpt-4", "gpt-3.5", "gpt-4o", "gpt-4-turbo"]):
            return "openai"
        
        # Anthropic models
        if any(m in model_lower for m in ["claude", "anthropic"]):
            return "anthropic"
        
        # Google models
        if any(m in model_lower for m in ["gemini", "google"]):
            return "google"
        
        # Ollama (local)
        if "llama" in model_lower or "local" in model_lower:
            return "ollama"
        
        # Default to OpenAI
        return "openai"


class AIClient:
    """AI client that routes requests to different providers."""
    
    def __init__(self):
        self.router = ModelRouter()
    
    def get_provider_for_model(self, model_name: str) -> str:
        """Get the provider for a model."""
        return self.router.get_provider_for_model(model_name)
    
    def get_api_key(self, provider_id: str) -> str | None:
        """Get API key for a provider from environment."""
        env_var = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
            "ollama": None,
            "openrouter": "OPENROUTER_API_KEY",
            "grok": "GROK_API_KEY",
            "unsloth": "UNSLOTH_API_KEY",
            "lms": "LMSTUDIO_API_KEY",
            "nous": "NOUS_API_KEY",
            "opencode_zen": "OPENCODE_ZEN_API_KEY",
            "opencode_go": "OPENCODE_GO_API_KEY",
        }.get(provider_id)
        
        if env_var:
            return os.environ.get(env_var)
        return None
    
    def chat(self, provider_id: str, model_name: str, messages: list[dict], **kwargs) -> dict:
        """Send a chat request to a provider."""
        # Return a mock response for testing
        return {
            "provider": provider_id,
            "model": model_name,
            "role": "assistant",
            "content": f"[Mock response from {provider_id}/{model_name}]",
            "usage": {"tokens_in": 10, "tokens_out": 20},
        }


__all__ = [
    "ChatMessage",
    "ChatSession", 
    "ModelInfo",
    "ModelRouter",
    "AIClient",
]
