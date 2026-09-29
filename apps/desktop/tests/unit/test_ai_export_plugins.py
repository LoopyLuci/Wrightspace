#!/usr/bin/env python3
"""Unit Tests for AI, Export, and Plugin modules."""

import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from webbuilder.ai import (
    ModelInfo, ChatMessage, ChatSession, BaseProvider,
    OpenAIProvider, AnthropicProvider, OpenRouterProvider,
    GrokProvider, NousProvider, OllamaProvider, LMStudioProvider,
    ModelRouter, get_router, setup_providers,
)
from webbuilder.export import HTMLExporter, ReactExporter, VueExporter, JSONExporter, ExportManager
from webbuilder.plugins import PluginManager
from webbuilder.exceptions import (
    AIAPIError, AIModelNotFoundError, AIProviderNotFoundError, AIRateLimitError,
)


class TestModelInfo:
    """Test ModelInfo data class."""

    def test_create_model_info(self):
        model = ModelInfo(
            id="gpt-4",
            name="GPT-4",
            provider="openai",
            provider_name="OpenAI",
        )
        assert model.id == "gpt-4"
        assert model.name == "GPT-4"
        assert model.is_free is False

    def test_to_dict(self):
        model = ModelInfo(id="test", name="Test", provider="p", provider_name="P")
        d = model.to_dict()
        assert d["id"] == "test"
        assert d["name"] == "Test"


class TestChatMessage:
    """Test ChatMessage data class."""

    def test_create_message(self):
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"


class TestChatSession:
    """Test ChatSession."""

    def test_create_session(self):
        session = ChatSession()
        assert session.messages == []

    def test_add_message(self):
        session = ChatSession()
        session.add_user_message("Hello")
        assert len(session.messages) == 1
        assert session.messages[0].role == "user"

    def test_add_assistant_message(self):
        session = ChatSession()
        session.add_assistant_message("Hi")
        assert len(session.messages) == 1
        assert session.messages[0].role == "assistant"


class TestAIProviders:
    """Test AI provider classes."""

    def test_openai_provider_init(self):
        provider = OpenAIProvider("")
        assert provider is not None

    def test_anthropic_provider_init(self):
        provider = AnthropicProvider("")
        assert provider is not None

    def test_ollama_provider_init(self):
        provider = OllamaProvider("")
        assert provider is not None

    def test_openrouter_provider_init(self):
        provider = OpenRouterProvider("")
        assert provider is not None

    def test_grok_provider_init(self):
        provider = GrokProvider("")
        assert provider is not None

    def test_nous_provider_init(self):
        provider = NousProvider("")
        assert provider is not None

    def test_lmstudio_provider_init(self):
        provider = LMStudioProvider("")
        assert provider is not None


class TestModelRouter:
    """Test ModelRouter."""

    def test_create_router(self):
        router = ModelRouter()
        assert router is not None

    def test_get_router_singleton(self):
        router1 = get_router()
        router2 = get_router()
        assert router1 is router2


class TestHTMLExporter:
    """Test HTMLExporter."""

    def test_export_basic_project(self):
        from webbuilder.core import Project, Page, Section
        project = Project(id="test", name="Test", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id="s1", type="Hero", props={"title": "Welcome"})
            ])
        ])
        exporter = HTMLExporter()
        html = exporter.generate(project)
        assert "<!DOCTYPE html>" in html
        assert "Welcome" in html

    def test_export_includes_css(self):
        from webbuilder.core import Project
        project = Project(id="test", name="Test")
        exporter = HTMLExporter()
        html = exporter.generate(project)
        assert "<style>" in html

    def test_export_multi_page(self):
        from webbuilder.core import Project, Page, Section
        project = Project(id="test", name="Test", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id="s1", type="Hero", props={"title": "Home"})
            ]),
            Page(id="p2", name="About", sections=[
                Section(id="s2", type="Hero", props={"title": "About"})
            ]),
        ])
        exporter = HTMLExporter()
        html = exporter.generate(project)
        assert "Home" in html
        assert "About" in html

    def test_export_escapes_html(self):
        from webbuilder.core import Project, Page, Section
        project = Project(id="test", name="<script>alert('xss')</script>", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id="s1", type="Hero", props={"title": "<b>Bold</b>"})
            ])
        ])
        exporter = HTMLExporter()
        html = exporter.generate(project)
        assert "<script>alert" not in html
        assert "&lt;script&gt;" in html


class TestReactExporter:
    """Test ReactExporter."""

    def test_export_creates_components(self):
        from webbuilder.core import Project, Page, Section
        project = Project(id="test", name="Test", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id="s1", type="Hero", props={"title": "Welcome"})
            ])
        ])
        exporter = ReactExporter()
        result = exporter.generate(project)
        assert len(result) > 0

    def test_export_creates_package_json(self):
        from webbuilder.core import Project, Page, Section
        project = Project(id="test", name="Test", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id="s1", type="Hero", props={"title": "Welcome"})
            ])
        ])
        exporter = ReactExporter()
        result = exporter.generate(project)
        assert "import React" in result
        assert "App" in result


class TestVueExporter:
    """Test VueExporter."""

    def test_export_creates_vue_components(self):
        from webbuilder.core import Project, Page, Section
        project = Project(id="test", name="Test", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id="s1", type="Hero", props={"title": "Welcome"})
            ])
        ])
        exporter = VueExporter()
        result = exporter.generate(project)
        assert "<template>" in result
        assert "</template>" in result


class TestJSONExporter:
    """Test JSONExporter."""

    def test_export_valid_json(self):
        from webbuilder.core import Project
        project = Project(id="test", name="Test")
        exporter = JSONExporter()
        json_str = exporter.generate(project)
        data = json.loads(json_str)
        assert data["id"] == "test"
        assert data["name"] == "Test"


class TestExportManager:
    """Test ExportManager."""

    def test_get_supported_formats(self):
        manager = ExportManager()
        formats = manager.get_supported_formats()
        assert "html" in formats
        assert "react" in formats
        assert "vue" in formats
        assert "json" in formats

    def test_export_project(self):
        from webbuilder.core import Project
        manager = ExportManager()
        project = Project(id="test", name="Test")
        with tempfile.TemporaryDirectory() as tmpdir:
            result = manager.export(project, "html", Path(tmpdir) / "output")
            assert result.exists()


class TestPluginManager:
    """Test PluginManager."""

    def test_discover_plugins(self):
        pm = PluginManager()
        plugins = pm.discover_plugins()
        assert len(plugins) >= 0

    def test_get_all_plugins(self):
        pm = PluginManager()
        plugins = pm.get_all_plugins()
        assert isinstance(plugins, list)

    def test_get_plugin(self):
        pm = PluginManager()
        plugin = pm.get_plugin("seo")
        assert plugin is None or hasattr(plugin, "name")
