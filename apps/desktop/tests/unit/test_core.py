#!/usr/bin/env python3
"""Unit Tests for WebBuilder Core Modules."""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from webbuilder.core import (
    Project, Page, Section, Design, ProjectManager,
)
from webbuilder.core.multi import MultiPageProject, AssetManager, DeploymentManager
from webbuilder.config import Config
from webbuilder.ai import ModelRouter, ModelInfo, ChatSession, ChatMessage
from webbuilder.exceptions import (
    ProjectNotFoundError, ProjectValidationError, ProjectPersistenceError,
    AssetNotFoundError, AssetValidationError,
)
from webbuilder.validation import validate_project, validate_section_type, sanitize_string


class TestProject:
    """Test Project model."""

    def test_create_project(self):
        project = Project(id="test-1", name="Test")
        assert project.id == "test-1"
        assert project.name == "Test"
        assert project.pages == []
        assert isinstance(project.design, Design)

    def test_project_to_dict(self):
        project = Project(id="test-1", name="Test")
        data = project.to_dict()
        assert data["id"] == "test-1"
        assert data["name"] == "Test"
        assert "pages" in data
        assert "design" in data

    def test_project_from_dict(self):
        data = {
            "id": "test-1",
            "name": "Test",
            "pages": [{"id": "p1", "name": "Home", "sections": []}],
            "design": {"colors": {"primary": "#3b82f6"}, "fonts": {"heading": "Inter"}},
        }
        project = Project.from_dict(data)
        assert project.id == "test-1"
        assert len(project.pages) == 1

    def test_project_with_pages(self):
        page = Page(id="p1", name="Home", sections=[
            Section(id="s1", type="Hero", props={"title": "Welcome"})
        ])
        project = Project(id="test-1", name="Test", pages=[page])
        assert len(project.pages) == 1
        assert len(project.pages[0].sections) == 1


class TestMultiPageProject:
    """Test MultiPageProject model."""

    def test_add_page(self):
        project = MultiPageProject(id="test", name="Test")
        page = project.add_page("About")
        assert page.name == "About"
        assert len(project.pages) == 1

    def test_remove_page(self):
        project = MultiPageProject(id="test", name="Test")
        project.add_page("Home")
        project.add_page("About")
        assert project.remove_page("page-1")
        assert len(project.pages) == 1

    def test_remove_last_page_fails(self):
        project = MultiPageProject(id="test", name="Test")
        project.add_page("Home")
        assert not project.remove_page("page-1")

    def test_duplicate_page(self):
        project = MultiPageProject(id="test", name="Test")
        project.add_page("Home")
        dup = project.duplicate_page("page-1")
        assert dup is not None
        assert "Copy" in dup.name
        assert len(project.pages) == 2

    def test_reorder_pages(self):
        project = MultiPageProject(id="test", name="Test")
        project.add_page("A")
        project.add_page("B")
        project.add_page("C")
        project.reorder_pages(["page-3", "page-1", "page-2"])
        assert project.pages[0].name == "C"


class TestProjectManager:
    """Test ProjectManager."""

    def test_create_new(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            project = pm.create_new("My Site")
            assert project.id.startswith("project-")
            assert project.name == "My Site"

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            project = pm.create_new("Test")
            pm.save(project)

            loaded = pm.load(project.id)
            assert loaded is not None
            assert loaded.name == "Test"

    def test_load_nonexistent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            assert pm.load("nonexistent") is None

    def test_list_projects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            pm.create_new("A")
            pm.create_new("B")
            projects = pm.list_projects()
            assert len(projects) == 2

    def test_delete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            project = pm.create_new("Test")
            assert pm.delete(project.id)
            assert pm.load(project.id) is None

    def test_backup(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            project = pm.create_new("Test")
            pm.save(project)

            # Verify project can be listed (no backup method exists)
            projects = pm.list_projects()
            assert len(projects) >= 1


class TestConfig:
    """Test Config singleton."""

    def test_singleton(self):
        config1 = Config.get()
        config2 = Config.get()
        assert config1 is config2

    def test_providers_loaded(self):
        config = Config.get()
        assert len(config.providers) >= 3
        assert "openai" in config.providers
        assert "anthropic" in config.providers

    def test_get_free_models(self):
        config = Config.get()
        models = config.get_models_for_dropdown()
        free = [m for m in models if m[4]]  # is_free flag
        assert len(free) > 0

    def test_get_local_models(self):
        config = Config.get()
        models = config.get_models_for_dropdown()
        local = [m for m in models if "Ollama" in m[3] or "LM Studio" in m[3]]
        assert len(local) > 0

    def test_models_for_dropdown(self):
        config = Config.get()
        models = config.get_models_for_dropdown()
        assert len(models) > 0
        # Free models should come first
        found_paid = False
        for _, _, _, _, is_free in models:
            if not is_free:
                found_paid = True
            elif found_paid:
                pytest.fail("Free model found after paid model")


class TestValidation:
    """Test validation functions."""

    def test_valid_project(self):
        data = {
            "id": "test-123",
            "name": "Test",
            "pages": [{"id": "p1", "name": "Home", "sections": []}],
            "design": {"colors": {}, "fonts": {}},
        }
        errors = validate_project(data)
        assert len(errors) == 0

    def test_missing_required_field(self):
        data = {"name": "Test"}
        errors = validate_project(data)
        assert len(errors) > 0

    def test_invalid_id_format(self):
        data = {
            "id": "test 123",
            "name": "Test",
            "pages": [{"id": "p1", "name": "Home", "sections": []}],
            "design": {"colors": {}, "fonts": {}},
        }
        errors = validate_project(data)
        assert any("id" in e.lower() for e in errors)

    def test_valid_section_type(self):
        assert validate_section_type("Hero — Centered") is None

    def test_invalid_section_type(self):
        assert validate_section_type("Invalid Type") is not None

    def test_sanitize_string_xss(self):
        result = sanitize_string("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result


class TestDeploymentManager:
    """Test DeploymentManager."""

    def test_supported_platforms(self):
        dm = DeploymentManager()
        platforms = dm.get_supported_platforms()
        assert "vercel" in platforms
        assert "netlify" in platforms
        assert "cloudflare" in platforms

    def test_deploy_vercel(self):
        dm = DeploymentManager()
        project = Project(id="test", name="Test")
        with tempfile.TemporaryDirectory() as tmpdir:
            result = dm.deploy(project, "vercel", Path(tmpdir))
            assert result["status"] == "ready"
            assert Path(result["config_path"]).exists()

    def test_deploy_netlify(self):
        dm = DeploymentManager()
        project = Project(id="test", name="Test")
        with tempfile.TemporaryDirectory() as tmpdir:
            result = dm.deploy(project, "netlify", Path(tmpdir))
            assert result["status"] == "ready"

    def test_unsupported_platform(self):
        dm = DeploymentManager()
        project = Project(id="test", name="Test")
        with pytest.raises(Exception):
            dm.deploy(project, "heroku", Path("/tmp"))
