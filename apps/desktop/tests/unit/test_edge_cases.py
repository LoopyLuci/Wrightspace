#!/usr/bin/env python3
"""Edge Case Tests for WebBuilder."""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from webbuilder.core import Project, Page, Section, ProjectManager
from webbuilder.export import HTMLExporter, ExportManager
from webbuilder.templates import TemplateManager
from webbuilder.forms import FormBuilder
from webbuilder.seo import SEOMetadata
from webbuilder.contrib.search import ProjectSearch
from webbuilder.contrib.performance import AutoSave, CrashRecovery, MemoryMonitor, PerformanceTimer
from webbuilder.validation import sanitize_string, is_valid_color, sanitize_filename


class TestEmptyInputs:
    """Test empty input handling."""

    def test_empty_project_name(self):
        project = Project(id="test", name="", pages=[])
        assert project.name == ""

    def test_empty_section_props(self):
        section = Section(id="s1", type="Hero", props={})
        assert section.props == {}

    def test_empty_page(self):
        page = Page(id="p1", name="Empty", sections=[])
        assert len(page.sections) == 0

    def test_export_empty_project(self):
        project = Project(id="test", name="Empty", pages=[])
        exporter = HTMLExporter()
        html = exporter.generate(project)
        assert "<!DOCTYPE html>" in html

    def test_export_page_with_no_sections(self):
        project = Project(id="test", name="Test", pages=[
            Page(id="p1", name="Empty", sections=[])
        ])
        exporter = HTMLExporter()
        html = exporter.generate(project)
        assert "<!DOCTYPE html>" in html

    def test_sanitize_empty_string(self):
        assert sanitize_string("") == ""

    def test_validate_empty_color(self):
        assert not is_valid_color("")


class TestUnicodeAndSpecialChars:
    """Test unicode and special character handling."""

    def test_unicode_project_name(self):
        project = Project(id="test", name="🚀 My Website 网站", pages=[])
        assert "🚀" in project.name

    def test_unicode_in_section_props(self):
        section = Section(id="s1", type="Hero", props={
            "title": "Bem-vindo 日本語 العربية"
        })
        assert "日本語" in section.props["title"]

    def test_unicode_export(self):
        project = Project(id="test", name="Test", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id="s1", type="Hero", props={"title": "Ünïcödé Tëst"})
            ])
        ])
        exporter = HTMLExporter()
        html = exporter.generate(project)
        assert "Ünïcödé" in html

    def test_emoji_in_project_name(self):
        project = Project(id="test", name="My 🚀 Project", pages=[])
        assert "🚀" in project.name

    def test_newlines_in_string(self):
        result = sanitize_string("line1\nline2\nline3")
        assert "\n" in result

    def test_tabs_in_string(self):
        result = sanitize_string("col1\tcol2\tcol3")
        assert "\t" in result


class TestBoundaryConditions:
    """Test boundary conditions."""

    def test_very_long_project_name(self):
        project = Project(id="test", name="A" * 1000, pages=[])
        assert len(project.name) == 1000

    def test_very_long_section_prop(self):
        section = Section(id="s1", type="Hero", props={
            "title": "A" * 10000
        })
        assert len(section.props["title"]) == 10000

    def test_max_sections_on_page(self):
        page = Page(id="p1", name="Max", sections=[
            Section(id=f"s{i}", type="Hero", props={"title": f"Section {i}"})
            for i in range(100)
        ])
        assert len(page.sections) == 100

    def test_max_pages_on_project(self):
        project = Project(id="test", name="Max", pages=[
            Page(id=f"p{i}", name=f"Page {i}", sections=[])
            for i in range(50)
        ])
        assert len(project.pages) == 50

    def test_special_chars_in_id(self):
        section = Section(id="s1-Test_123", type="Hero", props={})
        assert section.id == "s1-Test_123"


class TestMalformedData:
    """Test malformed data handling."""

    def test_none_props_handled(self):
        section = Section(id="s1", type="Hero", props={})
        section.props = {}
        assert section.props is not None

    def test_missing_optional_fields(self):
        project = Project(id="test", name="Test")
        assert project.pages == []

    def test_extra_fields_in_dict(self):
        data = {
            "id": "test",
            "name": "Test",
            "pages": [],
            "design": {},
            "extra_field": "should be ignored",
        }
        project = Project.from_dict(data)
        assert project.id == "test"

    def test_invalid_json_recovery(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            project = pm.create_new("Test")
            pm.save(project)
            
            # Corrupt the file
            file_path = Path(tmpdir) / f"{project.id}.json"
            file_path.write_text("not valid json{")
            
            # Should raise an error
            with pytest.raises(Exception):
                pm.load(project.id)


class TestColorValidation:
    """Test color validation edge cases."""

    def test_hex_3_chars(self):
        assert is_valid_color("#FFF")

    def test_hex_6_chars(self):
        assert is_valid_color("#3b82f6")

    def test_hex_8_chars_alpha(self):
        assert is_valid_color("#3b82f6FF")

    def test_rgb_values_at_boundary(self):
        assert is_valid_color("rgb(0, 0, 0)")
        assert is_valid_color("rgb(255, 255, 255)")

    def test_rgb_values_out_of_range(self):
        assert not is_valid_color("rgb(256, 0, 0)")
        assert not is_valid_color("rgb(-1, 0, 0)")

    def test_hsl_values_at_boundary(self):
        assert is_valid_color("hsl(0, 0%, 0%)")
        assert is_valid_color("hsl(360, 100%, 100%)")

    def test_hsl_values_out_of_range(self):
        assert not is_valid_color("hsl(361, 50%, 50%)")
        assert not is_valid_color("hsl(180, 101%, 50%)")

    def test_named_color(self):
        assert is_valid_color("red")
        assert is_valid_color("blue")

    def test_empty_color(self):
        assert not is_valid_color("")

    def test_malformed_rgb(self):
        assert not is_valid_color("rgb(abc, def, ghi)")


class TestURLValidation:
    """Test URL validation edge cases."""

    def test_http_url(self):
        from webbuilder.validation import sanitize_url
        assert sanitize_url("http://example.com")

    def test_https_url(self):
        from webbuilder.validation import sanitize_url
        assert sanitize_url("https://example.com")

    def test_url_with_path(self):
        from webbuilder.validation import sanitize_url
        assert sanitize_url("https://example.com/path/to/page")

    def test_url_with_query(self):
        from webbuilder.validation import sanitize_url
        assert sanitize_url("https://example.com?foo=bar&baz=qux")

    def test_url_with_port(self):
        from webbuilder.validation import sanitize_url
        assert sanitize_url("http://localhost:3000")

    def test_url_with_fragment(self):
        from webbuilder.validation import sanitize_url
        assert sanitize_url("https://example.com#section")

    def test_ftp_url_blocked(self):
        from webbuilder.validation import sanitize_url
        assert not sanitize_url("ftp://example.com")

    def test_file_url_blocked(self):
        from webbuilder.validation import sanitize_url
        assert not sanitize_url("file:///etc/passwd")

    def test_javascript_url_blocked(self):
        from webbuilder.validation import sanitize_url
        assert not sanitize_url("javascript:alert(1)")

    def test_empty_url(self):
        from webbuilder.validation import sanitize_url
        assert not sanitize_url("")

    def test_not_a_url(self):
        from webbuilder.validation import sanitize_url
        assert not sanitize_url("just some text")


class TestFormEdgeCases:
    """Test form edge cases."""

    def test_empty_form(self):
        fb = FormBuilder()
        form = fb.create_form("Empty")
        html = fb.to_html(form)
        assert "<form" in html

    def test_form_with_no_fields(self):
        fb = FormBuilder()
        form = fb.create_form("Empty")
        data = {}
        result = fb.submit_form(form.id, data)
        assert result["success"] is True

    def test_very_long_field_value(self):
        fb = FormBuilder()
        form = fb.create_form("Test")
        fb.add_field(form.id, "text", "Name")
        
        data = {"Name": "A" * 10000}
        result = fb.submit_form(form.id, data)
        assert result["success"] is True

    def test_special_chars_in_field_value(self):
        fb = FormBuilder()
        form = fb.create_form("Test")
        fb.add_field(form.id, "text", "Name")
        
        data = {"Name": "<script>alert(1)</script>"}
        result = fb.submit_form(form.id, data)
        assert result["success"] is True
        assert "<script>" not in result.get("data", {}).get("Name", "")

    def test_unicode_field_value(self):
        fb = FormBuilder()
        form = fb.create_form("Test")
        fb.add_field(form.id, "text", "Name")
        
        data = {"Name": "日本語テスト"}
        result = fb.submit_form(form.id, data)
        assert result["success"] is True
        # Check submission data via get_submissions
        subs = fb.get_submissions(form.id)
        assert len(subs) == 1
        assert subs[0]["data"]["Name"] == "日本語テスト"


class TestSearchEdgeCases:
    """Test search edge cases."""

    def test_empty_search_query(self):
        pm = ProjectManager()
        search = ProjectSearch(pm)
        results = search.search("")
        assert len(results) == 0

    def test_search_no_results(self):
        pm = ProjectManager()
        search = ProjectSearch(pm)
        project = Project(id="test", name="Test", pages=[])
        search.add_project(project)
        results = search.search("nonexistent")
        assert len(results) == 0

    def test_search_special_chars(self):
        pm = ProjectManager()
        search = ProjectSearch(pm)
        project = Project(id="test", name="Test <script>", pages=[])
        search.add_project(project)
        results = search.search("<script>")
        assert len(results) == 1

    def test_search_case_insensitive(self):
        pm = ProjectManager()
        search = ProjectSearch(pm)
        project = Project(id="test", name="UPPERCASE", pages=[])
        search.add_project(project)
        results = search.search("uppercase")
        assert len(results) == 1


class TestPerformanceEdgeCases:
    """Test performance edge cases."""

    def test_auto_save_rapid_mark_dirty(self):
        saves = []
        auto = AutoSave(lambda: saves.append(True), interval=0)
        
        for _ in range(100):
            auto.mark_dirty()
            auto.check_and_save()
        
        assert len(saves) == 100

    def test_crash_recovery_no_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            recovery = CrashRecovery(Path(tmpdir))
            assert not recovery.has_recovery()
            assert recovery.get_recovery() is None
            assert recovery.get_recovery_info() is None

    def test_memory_monitor_no_psutil(self):
        monitor = MemoryMonitor()
        result = monitor.get_memory_usage()
        assert "memory_mb" in result

    def test_performance_timer_fast_operation(self):
        from webbuilder.performance import PerformanceTimer
        with PerformanceTimer("fast", threshold_ms=1000) as timer:
            pass
        assert timer.elapsed_ms < 10

    def test_performance_timer_slow_operation(self):
        from webbuilder.performance import PerformanceTimer
        import time
        with PerformanceTimer("slow", threshold_ms=10) as timer:
            time.sleep(0.1)
        assert timer.elapsed_ms > 100
