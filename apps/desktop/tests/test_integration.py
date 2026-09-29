#!/usr/bin/env python3
"""Integration Tests: Full workflow tests for WebBuilder."""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_full_workflow():
    """Test the complete workflow: Create → Edit → Export → Verify."""
    from webbuilder.core import ProjectManager, Project, Page, Section, Design
    from webbuilder.export import HTMLExporter
    
    # Create
    pm = ProjectManager()
    p = pm.create_new("Integration Test")
    assert p.id, "Project ID should be set"
    assert p.name == "Integration Test"
    assert len(p.pages) == 1
    
    # Add sections
    p.pages[0].sections.append(Section(id="hero", type="Hero", props={"title": "Welcome", "subtitle": "Test"}))
    p.pages[0].sections.append(Section(id="features", type="Features", props={"title": "Features", "items": []}))
    p.pages[0].sections.append(Section(id="footer", type="Footer", props={"copyright": "© 2024"}))
    assert len(p.pages[0].sections) == 3
    
    # Save
    pm.save(p)
    
    # Load
    loaded = pm.load(p.id)
    assert loaded.id == p.id
    assert len(loaded.pages[0].sections) == 3
    
    # Export
    exporter = HTMLExporter()
    html = exporter.generate(loaded)
    assert "<!DOCTYPE html>" in html
    assert "Welcome" in html
    assert "Features" in html
    assert len(html) > 1000
    
    # Cleanup
    pm.delete(p.id)
    return True


def test_schema_versioning():
    """Test that all models have schema versioning."""
    from webbuilder.core import Project, Page, Section, Design
    
    s = Section(id="s1", type="Hero", props={"title": "Test"})
    s_dict = s.to_dict()
    assert "_schema" in s_dict
    assert "_version" in s_dict
    assert s_dict["_schema"] == "webbuilder/section"
    
    p = Page(id="p1", name="Home")
    p_dict = p.to_dict()
    assert "_schema" in p_dict
    assert p_dict["_schema"] == "webbuilder/page"
    
    d = Design()
    d_dict = d.to_dict()
    assert "_schema" in d_dict
    
    proj = Project(id="proj1", name="Test")
    proj_dict = proj.to_dict()
    assert "_schema" in proj_dict
    assert proj_dict["_schema"] == "webbuilder/project"
    
    return True


def test_serialization_roundtrip():
    """Test that serialization → deserialization preserves data."""
    from webbuilder.core import Project, Page, Section, Design
    
    # Create complex project
    original = Project(
        id="test-123",
        name="Test Project",
        pages=[
            Page(id="page-1", name="Home", sections=[
                Section(id="s1", type="Hero", props={"title": "Hello", "subtitle": "World"}),
                Section(id="s2", type="Features", props={"title": "Features", "items": []}),
            ]),
            Page(id="page-2", name="About", sections=[
                Section(id="s3", type="Hero", props={"title": "About Us"}),
            ]),
        ],
        design=Design(colors={"primary": "#ff0000"})
    )
    
    # Serialize
    data = original.to_dict()
    
    # Deserialize
    restored = Project.from_dict(data)
    
    # Verify
    assert restored.id == original.id
    assert restored.name == original.name
    assert len(restored.pages) == len(original.pages)
    assert len(restored.pages[0].sections) == len(original.pages[0].sections)
    assert restored.design.colors["primary"] == "#ff0000"
    
    return True


def test_validation():
    """Test project validation."""
    from webbuilder.core import Project, Page, Section, validate_project
    
    # Valid project
    valid = Project(id="v1", name="Valid", pages=[Page(id="p1", name="Home")])
    errors = validate_project(valid)
    assert len(errors) == 0
    
    # Invalid project (no pages)
    invalid = Project(id="i1", name="Invalid", pages=[])
    errors = validate_project(invalid)
    assert len(errors) > 0
    
    return True


def test_storage():
    """Test storage operations."""
    from webbuilder.core import ProjectManager, Project, Page
    
    pm = ProjectManager()
    
    # Create and save
    p = pm.create_new("Storage Test")
    project_id = p.id
    pm.save(p)
    
    # Load
    loaded = pm.load(project_id)
    assert loaded is not None
    assert loaded.name == "Storage Test"
    
    # List
    projects = pm.list_projects()
    assert any(p["id"] == project_id for p in projects)
    
    # Delete
    pm.delete(project_id)
    loaded = pm.load(project_id)
    assert loaded is None
    
    return True


def test_export_formats():
    """Test different export formats."""
    from webbuilder.core import Project, Page, Section
    from webbuilder.export import HTMLExporter, JSONExporter
    
    project = Project(id="exp1", name="Export Test", pages=[
        Page(id="p1", name="Home", sections=[
            Section(id="s1", type="Hero", props={"title": "Export"})
        ])
    ])
    
    # HTML
    html_exporter = HTMLExporter()
    html = html_exporter.generate(project)
    assert "<!DOCTYPE html>" in html
    assert "Export" in html
    
    # JSON
    json_exporter = JSONExporter()
    json_str = json_exporter.generate(project)
    data = json.loads(json_str)
    assert data["id"] == "exp1"
    
    return True


def test_templates():
    """Test template system."""
    from webbuilder.templates import TemplateManager
    
    tm = TemplateManager()
    templates = tm.get_all_templates()
    assert len(templates) > 0
    
    # Get specific template
    template = tm.get_template("saas-landing")
    assert template is not None
    assert template.name == "SaaS Landing Page"
    
    return True


def test_forms():
    """Test form builder."""
    from webbuilder.forms import FormBuilder
    
    fb = FormBuilder()
    form = fb.create_form("Contact")
    fb.add_field(form.id, "text", "Name", required=True)
    fb.add_field(form.id, "email", "Email", required=True)
    fb.add_field(form.id, "textarea", "Message")
    
    assert len(form.fields) == 3
    
    # Test validation
    errors = fb.validate_submission(form.id, {"Name": "", "Email": "invalid", "Message": ""})
    assert len(errors) > 0  # Should have errors for empty name and invalid email
    
    return True


def test_seo():
    """Test SEO analysis."""
    from webbuilder.seo import SEOMetadata, SEOAnalyzer
    
    meta = SEOMetadata(title="Test Page", description="A test page for SEO analysis")
    analyzer = SEOAnalyzer()
    
    html = "<html><head><title>Test</title></head><body><h1>Hello</h1></body></html>"
    result = analyzer.analyze(html, meta)
    
    assert "score" in result
    assert "issues" in result
    assert "recommendations" in result
    
    return True


def run_all_tests():
    """Run all integration tests."""
    import traceback
    
    tests = [
        ("Full Workflow", test_full_workflow),
        ("Schema Versioning", test_schema_versioning),
        ("Serialization Roundtrip", test_serialization_roundtrip),
        ("Validation", test_validation),
        ("Storage", test_storage),
        ("Export Formats", test_export_formats),
        ("Templates", test_templates),
        ("Forms", test_forms),
        ("SEO", test_seo),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except Exception as e:
            print(f"✗ {name}: {e}")
            traceback.print_exc()
            failed += 1
    
    print(f"\n{passed}/{passed + failed} tests passed")
    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
