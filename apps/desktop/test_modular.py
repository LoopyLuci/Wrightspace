"""Tests for the modular WebBuilder architecture."""

import sys
import os
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from webbuilder.core import (
    Config, Project, Page, Section, Design,
    ProjectManager, Provider, Model, ProviderType
)
from webbuilder.export import HTMLExporter, JSONExporter, ExportManager
from webbuilder.ai import AIClient, ChatSession, ChatMessage


def test_config():
    """Test configuration loading."""
    config = Config.get()
    assert len(config.providers) >= 7, f"Expected 7+ providers, got {len(config.providers)}"
    print(f"  ✓ {len(config.providers)} providers loaded")

    # Check required providers
    required = ["openai", "anthropic", "google", "ollama"]
    for pid in required:
        assert pid in config.providers, f"Missing provider: {pid}"
    print(f"  ✓ All required providers present")

    # Check free models
    free = config.get_all_free_models()
    assert len(free) > 0, "No free models found"
    print(f"  ✓ {len(free)} free models available")

    # Check local models
    local = config.get_all_local_models()
    assert len(local) > 0, "No local models found"
    print(f"  ✓ {len(local)} local models available")


def test_project():
    """Test project creation and serialization."""
    project = Project(
        id="test-123",
        name="Test Project",
        pages=[Page(id="p1", name="Home", sections=[
            Section(id="s1", type="Hero", props={"title": "Test"}),
            Section(id="s2", type="Footer", props={}),
        ])],
    )

    # Test dict conversion
    data = project.to_dict()
    assert data["id"] == "test-123"
    assert len(data["pages"][0]["sections"]) == 2
    print(f"  ✓ Project serialization works")

    # Test from_dict
    restored = Project.from_dict(data)
    assert restored.id == "test-123"
    assert len(restored.pages[0].sections) == 2
    print(f"  ✓ Project deserialization works")


def test_project_manager():
    """Test project persistence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pm = ProjectManager(Path(tmpdir))

        # Create
        project = pm.create_new("Persisted Project")
        assert project.id.startswith("project-")
        print(f"  ✓ Project created: {project.id}")

        # Save
        path = pm.save(project)
        assert path.exists()
        print(f"  ✓ Project saved to {path.name}")

        # Load
        loaded = pm.load(project.id)
        assert loaded is not None
        assert loaded.name == "Persisted Project"
        print(f"  ✓ Project loaded back")

        # List
        projects = pm.list_projects()
        assert len(projects) >= 1
        print(f"  ✓ Project listing works")

        # Delete
        assert pm.delete(project.id)
        assert pm.load(project.id) is None
        print(f"  ✓ Project deletion works")


def test_html_export():
    """Test HTML export."""
    project = Project(
        id="export-test",
        name="Export Test",
        pages=[Page(id="p1", name="Home", sections=[
            Section(id="s1", type="Navbar", props={"logo": "Brand", "links": ["Home", "About"]}),
            Section(id="s2", type="Hero — Centered", props={"title": "Welcome", "subtitle": "Test subtitle"}),
            Section(id="s3", type="Features — 3 Columns", props={
                "title": "Features",
                "items": [{"icon": "⚡", "title": "Fast", "description": "Very fast"}],
            }),
            Section(id="s4", type="Footer", props={"copyright": "© 2024"}),
        ])],
    )

    exporter = HTMLExporter()
    html = exporter.generate(project)

    assert "<!DOCTYPE html>" in html
    assert "Export Test" in html
    assert "Welcome" in html
    assert "@media" in html
    assert len(html) > 5000
    print(f"  ✓ HTML export: {len(html)} chars, all sections present")


def test_json_export():
    """Test JSON export."""
    project = Project(
        id="json-test",
        name="JSON Test",
        pages=[Page(id="p1", name="Home", sections=[
            Section(id="s1", type="Hero", props={"title": "Test"}),
        ])],
    )

    exporter = JSONExporter()
    json_str = exporter.generate(project)
    data = json.loads(json_str)

    assert data["id"] == "json-test"
    assert len(data["pages"][0]["sections"]) == 1
    print(f"  ✓ JSON export valid")


def test_export_manager():
    """Test export manager."""
    manager = ExportManager()
    formats = manager.get_supported_formats()
    assert "html" in formats
    assert "json" in formats
    print(f"  ✓ Export formats: {formats}")


def test_ai_client():
    """Test AI client routing."""
    client = AIClient()

    # Test provider lookup
    provider_id = client.get_provider_for_model("gpt-4o")
    assert provider_id == "openai"
    print(f"  ✓ Model routing works")

    # Test API key retrieval
    os.environ["OPENAI_API_KEY"] = "test-key"
    key = client.get_api_key("openai")
    assert key == "test-key"
    print(f"  ✓ API key retrieval works")

    # Test chat session
    session = ChatSession("You are a helpful assistant.")
    session.add_user_message("Hello")
    assert len(session.messages) == 2
    print(f"  ✓ Chat session works")


def test_plugins():
    """Test plugin system."""
    from webbuilder.plugins import SEOPlugin, AnalyticsPlugin, AccessibilityPlugin

    project = Project(
        id="plugin-test",
        name="Plugin Test",
        pages=[Page(id="p1", name="Home", sections=[
            Section(id="s1", type="Hero", props={"title": "Test"}),
        ])],
    )

    seo = SEOPlugin()
    result = seo.analyze_project(project)
    assert "score" in result
    assert "issues" in result
    print(f"  ✓ SEO plugin: score={result['score']}")

    analytics = AnalyticsPlugin()
    analytics.track_event("test", {"data": 123})
    assert len(analytics.get_events()) == 1
    print(f"  ✓ Analytics plugin works")

    a11y = AccessibilityPlugin()
    result = a11y.check_project(project)
    assert "score" in result
    print(f"  ✓ Accessibility plugin: score={result['score']}")


def test_provider_dropdown():
    """Test model dropdown sorting (free first)."""
    config = Config.get()
    models = config.get_models_for_dropdown()

    # Free models should come first
    found_paid = False
    for provider_id, model_id, name, context, is_free in models:
        if not is_free:
            found_paid = True
        elif found_paid:
            assert False, "Free model found after paid model"
    print(f"  ✓ Model dropdown: {len(models)} models, free first")


if __name__ == "__main__":
    print("\n=== WebBuilder Modular Architecture Tests ===\n")

    tests = [
        ("Config", test_config),
        ("Project", test_project),
        ("Project Manager", test_project_manager),
        ("HTML Export", test_html_export),
        ("JSON Export", test_json_export),
        ("Export Manager", test_export_manager),
        ("AI Client", test_ai_client),
        ("Plugins", test_plugins),
        ("Provider Dropdown", test_provider_dropdown),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        print(f"\n{name}:")
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  ❌ {e}")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    print(f"{'=' * 50}")

    if failed > 0:
        sys.exit(1)
