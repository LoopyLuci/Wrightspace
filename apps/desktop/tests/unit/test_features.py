#!/usr/bin/env python3
"""Unit Tests for Templates, Forms, SEO, Search, and Utility modules."""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from webbuilder.templates import TemplateManager, Template
from webbuilder.forms import FormBuilder, FormField
from webbuilder.seo import SEOMetadata, SitemapGenerator, RobotsTxtGenerator, SEOAnalyzer
from webbuilder.custom_code import CustomCodeManager, CustomCode
from webbuilder.contrib.search import ProjectSearch, SearchIndex
from webbuilder.contrib.analytics import AnalyticsTracker, AnalyticsEvent
from webbuilder.contrib.import_export import ProjectImporter, ProjectExporter, BackupManager
from webbuilder.contrib.performance import AutoSave, CrashRecovery, MemoryMonitor, PerformanceTimer
from webbuilder.validation import sanitize_string, sanitize_url, is_valid_color, sanitize_filename
from webbuilder.core import Project, Page, Section, ProjectManager


class TestTemplateManager:
    """Test TemplateManager."""

    def test_list_templates(self):
        tm = TemplateManager()
        templates = tm.get_all_templates()
        assert len(templates) > 0

    def test_list_categories(self):
        tm = TemplateManager()
        categories = tm.get_categories()
        assert len(categories) > 0

    def test_get_template(self):
        tm = TemplateManager()
        template = tm.get_template("saas-landing")
        assert template is not None
        assert "SaaS" in template.name

    def test_search_templates(self):
        tm = TemplateManager()
        results = tm.search_templates("portfolio")
        assert len(results) > 0

    def test_filter_by_category(self):
        tm = TemplateManager()
        results = tm.get_templates_by_category("Business")
        assert all(t.category == "Business" for t in results)

    def test_apply_template(self):
        tm = TemplateManager()
        result = tm.create_project_from_template("saas-landing", "test-1", "My Project")
        assert result is not None


class TestFormBuilder:
    """Test FormBuilder."""

    def test_create_form(self):
        fb = FormBuilder()
        form = fb.create_form("Contact Form")
        assert form.name == "Contact Form"

    def test_add_text_field(self):
        fb = FormBuilder()
        form = fb.create_form("Test")
        field = fb.add_field(form.id, "text", "Name")
        assert field.label == "Name"
        assert field.type == "text"

    def test_add_email_field(self):
        fb = FormBuilder()
        form = fb.create_form("Test")
        field = fb.add_field(form.id, "email", "Email")
        assert field.type == "email"

    def test_add_select_field(self):
        fb = FormBuilder()
        form = fb.create_form("Test")
        field = fb.add_field(form.id, "select", "Country", options=["USA", "UK", "Canada"])
        assert len(field.options) == 3

    def test_required_validation(self):
        fb = FormBuilder()
        form = fb.create_form("Test")
        fb.add_field(form.id, "text", "Name", required=True)
        errors = fb.validate_submission(form.id, {})
        assert len(errors) > 0

    def test_email_validation(self):
        fb = FormBuilder()
        form = fb.create_form("Test")
        fb.add_field(form.id, "email", "Email")
        # validate_submission uses field.id as key, not label
        field = form.fields[0]
        errors = fb.validate_submission(form.id, {field.id: "not-an-email"})
        assert len(errors) > 0
        errors = fb.validate_submission(form.id, {field.id: "valid@email.com"})
        assert len(errors) == 0

    def test_form_submission(self):
        fb = FormBuilder()
        form = fb.create_form("Test")
        fb.add_field(form.id, "text", "Name", required=True)
        fb.add_field(form.id, "email", "Email", required=True)
        
        # Valid submission - use field IDs as keys
        name_field = form.fields[0]
        email_field = form.fields[1]
        data = {name_field.id: "John", email_field.id: "john@example.com"}
        result = fb.submit_form(form.id, data)
        assert result["success"]

        # Invalid submission
        data = {name_field.id: "", email_field.id: "invalid"}
        result = fb.submit_form(form.id, data)
        assert not result["success"]

    def test_form_to_html(self):
        fb = FormBuilder()
        form = fb.create_form("Test")
        fb.add_field(form.id, "text", "Name", required=True)
        html = fb.to_html(form)
        assert "<form" in html
        assert "Name" in html


class TestSEOMetadata:
    """Test SEOMetadata."""

    def test_create_metadata(self):
        meta = SEOMetadata(
            title="My Page",
            description="Page description",
        )
        assert meta.title == "My Page"

    def test_to_meta_tags(self):
        meta = SEOMetadata(title="Test", description="Desc")
        html = meta.to_meta_tags()
        assert "<title>Test</title>" in html
        assert 'content="Desc"' in html

    def test_to_structured_data(self):
        meta = SEOMetadata(title="Test", description="Desc", structured_data={"name": "Test", "url": "https://example.com"})
        sd = meta.to_structured_data()
        assert '"name"' in sd
        assert 'Test' in sd

    def test_validate_good(self):
        meta = SEOMetadata(
            title="My Website - Home",
            description="Welcome to my website. Build something amazing with our tools.",
        )
        errors = meta.validate()
        assert len(errors) == 0

    def test_validate_short_title(self):
        meta = SEOMetadata(title="Hi", description="A" * 200)
        errors = meta.validate()
        assert len(errors) > 0


class TestSitemapGenerator:
    """Test SitemapGenerator."""

    def test_generate_sitemap(self):
        gen = SitemapGenerator()
        xml = gen.generate()
        assert "<urlset" in xml

    def test_save_sitemap(self):
        gen = SitemapGenerator()
        with tempfile.TemporaryDirectory() as tmpdir:
            gen.save(Path(tmpdir) / "sitemap.xml")
            assert (Path(tmpdir) / "sitemap.xml").exists()


class TestRobotsTxtGenerator:
    """Test RobotsTxtGenerator."""

    def test_generate_robots(self):
        gen = RobotsTxtGenerator()
        gen.add_rule("User-agent: *", allow=["/"], disallow=["/private"])
        content = gen.generate()
        assert "User-agent: *" in content


class TestSEOAnalyzer:
    """Test SEOAnalyzer."""

    def test_analyze_good_page(self):
        meta = SEOMetadata(
            title="My Website - Home",
            description="Welcome to my website. Build something amazing with our tools.",
        )
        analyzer = SEOAnalyzer()
        result = analyzer.analyze("<html><body>Test</body></html>", meta)
        assert "score" in result


class TestCustomCodeManager:
    """Test CustomCodeManager."""

    def test_set_custom_code(self):
        manager = CustomCodeManager()
        code = CustomCode(
            html="<div>Hello</div>",
            css="",
            js="",
            head_tags="",
            footer_scripts="",
        )
        errors = manager.set("project-1", code)
        assert len(errors) == 0

    def test_get_custom_code(self):
        manager = CustomCodeManager()
        code = CustomCode(html="<div>Hello</div>", css="", js="", head_tags="", footer_scripts="")
        manager.set("project-1", code)
        result = manager.get("project-1")
        assert result is not None

    def test_delete_custom_code(self):
        manager = CustomCodeManager()
        code = CustomCode(html="<div>Delete me</div>", css="", js="", head_tags="", footer_scripts="")
        manager.set("project-1", code)
        assert manager.delete("project-1") is True
        # get returns None when not found
        result = manager.get("project-1")
        assert result is None

    def test_export_code(self):
        manager = CustomCodeManager()
        code = CustomCode(html="", css="body { color: red; }", js="", head_tags="", footer_scripts="")
        manager.set("project-1", code)
        exported = manager.export_code("project-1")
        assert isinstance(exported, dict)


class TestProjectSearch:
    """Test ProjectSearch."""

    def test_add_project(self):
        pm = ProjectManager()
        search = ProjectSearch(pm)
        project = Project(id="test-1", name="Test Site", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id="s1", type="Hero", props={"title": "Welcome to our platform"})
            ])
        ])
        search.add_project(project)

    def test_search_projects(self):
        pm = ProjectManager()
        search = ProjectSearch(pm)
        project = Project(id="test-1", name="Test Site", pages=[])
        search.add_project(project)
        results = search.search("test")
        assert len(results) > 0

    def test_search_by_section_content(self):
        pm = ProjectManager()
        search = ProjectSearch(pm)
        project = Project(id="test-1", name="Test", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id="s1", type="Hero", props={"title": "Amazing Features"})
            ])
        ])
        search.add_project(project)
        results = search.search("features")
        assert len(results) > 0

    def test_remove_project(self):
        pm = ProjectManager()
        search = ProjectSearch(pm)
        project = Project(id="test-1", name="Test", pages=[])
        search.add_project(project)
        search.remove_project("test-1")


class TestAnalyticsTracker:
    """Test AnalyticsTracker."""

    def test_track_event(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = AnalyticsTracker(Path(tmpdir))
            tracker.track("project_created", {"project_id": "test-1"})
            assert len(tracker.events) == 1

    def test_get_events(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = AnalyticsTracker(Path(tmpdir))
            tracker.track("project_created", {})
            tracker.track("project_exported", {})
            events = tracker.get_events("project_created")
            assert len(events) == 1

    def test_get_stats(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = AnalyticsTracker(Path(tmpdir))
            tracker.track("project_created", {})
            tracker.track("project_exported", {})
            stats = tracker.get_stats()
            assert stats["event_counts"]["project_created"] == 1
            assert stats["event_counts"]["project_exported"] == 1


class TestImportExport:
    """Test ProjectImporter and ProjectExporter."""

    def test_export_project_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            exporter = ProjectExporter(pm)
            project = pm.create_new("Test")
            pm.save(project)
            path = exporter.export_to_json(project.id, Path(tmpdir) / f"{project.id}.json")
            assert path.exists()
            data = json.loads(path.read_text())
            assert data["name"] == "Test"

    def test_import_project_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            exporter = ProjectExporter(pm)
            importer = ProjectImporter(pm)
            project = pm.create_new("Test")
            pm.save(project)
            path = exporter.export_to_json(project.id, Path(tmpdir) / f"{project.id}.json")
            data = json.loads(path.read_text())
            imported = importer.import_from_json(data)
            assert imported.name == "Test"

    def test_export_project_zip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            exporter = ProjectExporter(pm)
            project = pm.create_new("Test")
            pm.save(project)
            path = exporter.export_to_zip([project.id], Path(tmpdir) / "projects.zip")
            assert path.exists()
            assert path.suffix == ".zip"

    def test_import_project_zip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            exporter = ProjectExporter(pm)
            importer = ProjectImporter(pm)
            project = pm.create_new("Test")
            pm.save(project)
            path = exporter.export_to_zip([project.id], Path(tmpdir) / "projects.zip")
            imported = importer.import_from_zip(path)
            assert len(imported) > 0

    def test_backup_manager(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            project = pm.create_new("Test")
            pm.save(project)
            bm = BackupManager(Path(tmpdir) / "backups")
            bm.create_backup(pm)
            backups = bm.list_backups()
            assert len(backups) > 0


class TestPerformanceModules:
    """Test AutoSave, CrashRecovery, MemoryMonitor."""

    def test_auto_save_dirty_tracking(self):
        saves = []
        auto = AutoSave(lambda: saves.append(True), interval=0)
        auto.mark_dirty()
        auto.check_and_save()
        assert len(saves) == 1

    def test_auto_save_not_dirty(self):
        saves = []
        auto = AutoSave(lambda: saves.append(True), interval=0)
        auto.check_and_save()
        assert len(saves) == 0

    def test_auto_save_force(self):
        saves = []
        auto = AutoSave(lambda: saves.append(True), interval=60)
        auto.force_save()
        assert len(saves) == 1

    def test_crash_recovery_save(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            recovery = CrashRecovery(Path(tmpdir))
            recovery.save_session({"id": "1", "name": "Test"})
            assert recovery.has_recovery()

    def test_crash_recovery_restore(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            recovery = CrashRecovery(Path(tmpdir))
            recovery.save_session({"id": "1", "name": "Test"})
            data = recovery.get_recovery()
            assert data is not None
            assert data.get("project", {}).get("name") == "Test"

    def test_crash_recovery_clear(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            recovery = CrashRecovery(Path(tmpdir))
            recovery.save_session({"id": "1", "name": "Test"})
            recovery.clear_recovery()
            assert not recovery.has_recovery()

    def test_memory_monitor(self):
        monitor = MemoryMonitor()
        result = monitor.get_memory_usage()
        assert "memory_mb" in result
        assert "warning" in result
        assert "critical" in result

    def test_performance_timer(self):
        with PerformanceTimer("test_op", threshold_ms=1000) as timer:
            pass
        assert timer.elapsed_ms < 1000
