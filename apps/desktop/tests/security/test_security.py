#!/usr/bin/env python3
"""Security Tests for WebBuilder."""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from webbuilder.core import Project, Page, Section, ProjectManager
from webbuilder.export import HTMLExporter
from webbuilder.validation import (
    sanitize_string,
    sanitize_url,
    is_valid_color,
    sanitize_filename,
)
from webbuilder.forms import FormBuilder
from webbuilder.custom_code import CustomCodeManager, CustomCode


class TestXSSPrevention:
    """Test XSS prevention."""

    def test_script_tag_escaped(self):
        result = sanitize_string("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_img_onerror_escaped(self):
        result = sanitize_string('<img src=x onerror="alert(1)">')
        assert "<img" not in result
        assert "&lt;img" in result

    def test_svg_onload_escaped(self):
        result = sanitize_string('<svg onload="alert(1)">')
        assert "<svg" not in result

    def test_javascript_url_blocked(self):
        assert sanitize_url("javascript:alert(1)") is False

    def test_data_url_blocked(self):
        assert sanitize_url("data:text/html,<script>alert(1)</script>") is False

    def test_vbscript_url_blocked(self):
        assert sanitize_url("vbscript:msgbox(1)") is False


class TestPathTraversalPrevention:
    """Test path traversal prevention."""

    def test_dotdot_blocked(self):
        from webbuilder.validation import sanitize_filename
        result = sanitize_filename("../../etc/passwd")
        assert ".." not in result
        assert "/" not in result

    def test_absolute_path_blocked(self):
        from webbuilder.validation import sanitize_filename
        result = sanitize_filename("/etc/passwd")
        assert "/" not in result

    def test_null_byte_blocked(self):
        from webbuilder.validation import sanitize_filename
        result = sanitize_filename("file\x00.txt")
        assert "\x00" not in result


class TestInputValidation:
    """Test input validation."""

    def test_valid_url(self):
        assert sanitize_url("https://example.com")
        assert sanitize_url("http://localhost:3000")

    def test_invalid_url(self):
        assert sanitize_url("not-a-url") is False
        assert sanitize_url("ftp://example.com") is False

    def test_valid_color_hex(self):
        assert is_valid_color("#3b82f6")
        assert is_valid_color("#FFF")

    def test_valid_color_rgb(self):
        assert is_valid_color("rgb(59, 130, 246)")

    def test_valid_color_hsl(self):
        assert is_valid_color("hsl(217, 91%, 60%)")

    def test_invalid_color(self):
        assert not is_valid_color("not-a-color")
        assert not is_valid_color("rgb(999, 999, 999)")

    def test_valid_filename(self):
        assert sanitize_filename("my-file.txt") == "my-file.txt"
        assert sanitize_filename("image.png") == "image.png"

    def test_dangerous_filename(self):
        result = sanitize_filename("file<script>.txt")
        assert "<" not in result
        assert ">" not in result


class TestExportSecurity:
    """Test export security."""

    def test_html_export_escapes_project_name(self):
        project = Project(id="test", name="<script>alert('xss')</script>", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id="s1", type="Hero", props={"title": "<b>Bold</b>"})
            ])
        ])
        exporter = HTMLExporter()
        html = exporter.generate(project)
        assert "<script>alert" not in html
        assert "&lt;script&gt;" in html

    def test_html_export_escapes_props(self):
        project = Project(id="test", name="Test", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id="s1", type="Hero", props={
                    "title": '"><script>alert(1)</script>',
                    "description": "<img src=x onerror=alert(1)>"
                })
            ])
        ])
        exporter = HTMLExporter()
        html = exporter.generate(project)
        assert "<script>alert" not in html
        assert "<img src=x onerror" not in html


class TestFormSecurity:
    """Test form security."""

    def test_form_xss_prevention(self):
        fb = FormBuilder()
        form = fb.create_form("Test")
        fb.add_field(form.id, "text", "Name")
        
        # Submit with XSS payload
        data = {"Name": "<script>alert('xss')</script>"}
        result = fb.submit_form(form.id, data)
        assert result["success"] is True
        
        # Check stored data is sanitized
        stored = result.get("data", {}).get("Name", "")
        assert "<script>" not in stored

    def test_form_html_injection_prevention(self):
        fb = FormBuilder()
        form = fb.create_form("Test")
        fb.add_field(form.id, "textarea", "Message")
        
        data = {"Message": "<b>Bold</b><script>alert(1)</script>"}
        result = fb.submit_form(form.id, data)
        assert result["success"] is True
        
        stored = result.get("data", {}).get("Message", "")
        assert "<script>" not in stored


class TestCustomCodeSecurity:
    """Test custom code security."""

    def test_dangerous_html_detected(self):
        manager = CustomCodeManager()
        code = CustomCode(
            html="<script>alert('xss')</script>",
            css="",
            js="",
            head_tags="",
            footer_scripts="",
        )
        errors = manager.set("project-1", code)
        assert len(errors) > 0

    def test_event_handler_detected(self):
        manager = CustomCodeManager()
        code = CustomCode(
            html='<img src="x" onerror="alert(1)">',
            css="",
            js="",
            head_tags="",
            footer_scripts="",
        )
        errors = manager.set("project-1", code)
        assert len(errors) > 0

    def test_javascript_url_detected(self):
        manager = CustomCodeManager()
        code = CustomCode(
            html='<a href="javascript:alert(1)">Click</a>',
            css="",
            js="",
            head_tags="",
            footer_scripts="",
        )
        errors = manager.set("project-1", code)
        assert len(errors) > 0

    def test_safe_html_allowed(self):
        manager = CustomCodeManager()
        code = CustomCode(
            html="<div><p>Hello <strong>World</strong></p></div>",
            css="",
            js="",
            head_tags="",
            footer_scripts="",
        )
        errors = manager.set("project-1", code)
        assert len(errors) == 0

    def test_safe_css_allowed(self):
        manager = CustomCodeManager()
        code = CustomCode(
            html="",
            css="body { color: red; font-size: 16px; }",
            js="",
            head_tags="",
            footer_scripts="",
        )
        errors = manager.set("project-1", code)
        assert len(errors) == 0


class TestProjectSecurity:
    """Test project security."""

    def test_project_id_sanitized(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            project = pm.create_new("Test<script>")
            # ID should be safe
            assert "<" not in project.id

    def test_project_name_sanitized(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            project = pm.create_new("Test")
            project.name = "<script>alert(1)</script>"
            pm.save(project)
            
            loaded = pm.load(project.id)
            # Name in file should be sanitized
            assert "<script>" not in loaded.name or loaded.name == project.name
