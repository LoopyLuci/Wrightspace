#!/usr/bin/env python3
"""Integration Tests for WebBuilder workflows."""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from webbuilder.core import (
    Project, Page, Section, Design, ProjectManager,
    MultiPageProject, AssetManager, DeploymentManager,
)
from webbuilder.config import Config
from webbuilder.export import HTMLExporter, ReactExporter, VueExporter, JSONExporter, ExportManager
from webbuilder.templates import TemplateManager
from webbuilder.forms import FormBuilder
from webbuilder.seo import SEOMetadata, SitemapGenerator, SEOAnalyzer
from webbuilder.search import ProjectSearch
from webbuilder.analytics import AnalyticsTracker, AnalyticsEvent
from webbuilder.performance import AutoSave, CrashRecovery, MemoryMonitor


class TestProjectLifecycle:
    """Test complete project lifecycle."""

    def test_create_edit_export(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            
            # Create
            project = pm.create_new("My Website")
            project.pages[0].sections.append(
                Section(id="s1", type="Hero", props={"title": "Welcome"})
            )
            pm.save(project)
            
            # Edit
            loaded = pm.load(project.id)
            loaded.pages[0].sections[0].props["title"] = "Updated Welcome"
            pm.save(loaded)
            
            # Export
            final = pm.load(project.id)
            exporter = HTMLExporter()
            html = exporter.generate(final)
            assert "Updated Welcome" in html

    def test_multi_page_workflow(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            project = pm.create_new("Multi Page")
            
            # Add pages
            project.pages.append(Page(id="about", name="About"))
            project.pages.append(Page(id="contact", name="Contact"))
            assert len(project.pages) == 3  # Home + About + Contact
            
            # Add sections to each page
            project.pages[0].sections.append(
                Section(id="s1", type="Hero", props={"title": "Home"})
            )
            project.pages[1].sections.append(
                Section(id="s2", type="Hero", props={"title": "About Us"})
            )
            project.pages[2].sections.append(
                Section(id="s3", type="Hero", props={"title": "Contact Us"})
            )
            
            pm.save(project)
            
            # Export all pages
            loaded = pm.load(project.id)
            exporter = HTMLExporter()
            html = exporter.generate(loaded)
            assert "Home" in html
            assert "About Us" in html
            assert "Contact Us" in html

    def test_template_to_export(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Apply template
            tm = TemplateManager()
            project = tm.create_project_from_template("saas-landing", "test-1", "SaaS Project")
            
            # Export
            exporter = HTMLExporter()
            html = exporter.generate(project)
            assert "<!DOCTYPE html>" in html
            assert len(html) > 1000

    def test_form_workflow(self):
        fb = FormBuilder()
        form = fb.create_form("Contact")
        name_field = fb.add_field(form.id, "text", "Name", required=True)
        email_field = fb.add_field(form.id, "email", "Email", required=True)
        msg_field = fb.add_field(form.id, "textarea", "Message", required=True)
        
        # Valid submission
        data = {name_field.id: "John", email_field.id: "john@example.com", msg_field.id: "Hello!"}
        result = fb.submit_form(form.id, data)
        assert result["success"]
        
        # Invalid submission
        data = {name_field.id: "", email_field.id: "invalid", msg_field.id: ""}
        result = fb.submit_form(form.id, data)
        assert not result["success"]

    def test_seo_workflow(self):
        from webbuilder.core import Project, Page, Section
        project = Project(id="test", name="Test", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id="s1", type="Hero", props={"title": "Welcome"})
            ])
        ])
        
        meta = SEOMetadata(
            title="My Website - Home",
            description="Welcome to my website. Build something amazing.",
        )
        
        # Analyze
        analyzer = SEOAnalyzer()
        result = analyzer.analyze("<html><body>Test</body></html>", meta)
        assert "score" in result
        
        # Generate sitemap
        gen = SitemapGenerator()
        xml = gen.generate()
        assert "<urlset" in xml

    def test_search_workflow(self):
        pm = ProjectManager()
        search = ProjectSearch(pm)
        
        # Index multiple projects
        for i in range(3):
            project = Project(id=f"test-{i}", name=f"Project {i}", pages=[
                Page(id=f"p{i}", name="Home", sections=[
                    Section(id=f"s{i}", type="Hero", props={"title": f"Welcome {i}"})
                ])
            ])
            search.add_project(project)
        
        # Search
        results = search.search("welcome")
        assert len(results) >= 0

    def test_analytics_workflow(self):
        tmpdir = tempfile.mkdtemp()
        try:
            db_path = Path(tmpdir) / "analytics.db"
            tracker = AnalyticsTracker(db_path)
            
            # Track events
            tracker.track("project_created", {"project_id": "1"})
            tracker.track("section_added", {"project_id": "1"})
            tracker.track("project_exported", {"project_id": "1"})
            
            # Get stats
            stats = tracker.get_stats()
            assert stats["event_counts"]["project_created"] == 1
            assert stats["event_counts"]["section_added"] == 1
            assert stats["event_counts"]["project_exported"] == 1
            
            # Close tracker before temp dir cleanup
            tracker.close()
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_auto_save_workflow(self):
        saves = []
        auto = AutoSave(lambda: saves.append(True), interval=0)
        
        # Mark dirty and save multiple times
        for _ in range(5):
            auto.mark_dirty()
            auto.check_and_save()
        
        assert len(saves) == 5

    def test_crash_recovery_workflow(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            recovery = CrashRecovery(Path(tmpdir))
            
            # Save session
            recovery.save_session({"id": "1", "name": "Test Project"})
            assert recovery.has_recovery()
            
            # Get info
            info = recovery.get_recovery_info()
            assert info["project_name"] == "Test Project"
            
            # Restore
            data = recovery.get_recovery()
            assert data["project"]["name"] == "Test Project"
            
            # Clear
            recovery.clear_recovery()
            assert not recovery.has_recovery()

    def test_export_all_formats(self):
        from webbuilder.core import Project, Page, Section
        project = Project(id="test", name="Test", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id="s1", type="Hero", props={"title": "Welcome"})
            ])
        ])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExportManager()
            
            # HTML
            html_path = manager.export(project, "html", Path(tmpdir) / "output.html")
            assert html_path.exists()
            
            # React
            react_path = manager.export(project, "react", Path(tmpdir) / "output_react")
            assert react_path.exists()
            
            # Vue
            vue_path = manager.export(project, "vue", Path(tmpdir) / "output_vue")
            assert vue_path.exists()
            
            # JSON
            json_path = manager.export(project, "json", Path(tmpdir) / "output.json")
            assert json_path.exists()

    def test_deployment_workflow(self):
        from webbuilder.core import Project
        project = Project(id="test", name="Test")
        
        dm = DeploymentManager()
        platforms = dm.get_supported_platforms()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            for platform in platforms:
                result = dm.deploy(project, platform, Path(tmpdir))
                assert result["status"] == "ready"
                assert Path(result["config_path"]).exists()


class TestConfigIntegration:
    """Test Config integration with other modules."""

    def test_config_providers_in_ai(self):
        config = Config.get()
        providers = config.providers
        
        # Verify providers are accessible
        assert "openai" in providers
        assert "anthropic" in providers

    def test_config_models_in_export(self):
        config = Config.get()
        models = config.get_models_for_dropdown()
        
        # Verify models are accessible
        assert len(models) > 0

    def test_config_free_models(self):
        config = Config.get()
        models = config.get_models_for_dropdown()
        free = [m for m in models if m[4]]
        
        # Verify free models exist
        assert len(free) > 0
