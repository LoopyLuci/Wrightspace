"""Tests for WebBuilder error handling, validation, and logging."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from webbuilder.core import Project, Page, Section, ProjectManager
from webbuilder.exceptions import (
    ProjectNotFoundError,
    ProjectValidationError,
    ProjectPersistenceError,
    AssetNotFoundError,
    AssetValidationError,
    AssetStorageError,
    DeploymentPlatformNotSupportedError,
    SectionTypeNotFoundError,
    ExportFormatNotSupportedError,
    AIModelNotFoundError,
    PathTraversalError,
    InputSanitizationError,
    SchemaValidationError,
)
from webbuilder.validation import (
    validate_project,
    validate_section_type,
    validate_section_props,
    sanitize_string,
    sanitize_filename,
    sanitize_path,
    sanitize_url,
    sanitize_color,
    validate_image_file,
    validate_font_file,
    _is_valid_color,
)
from webbuilder.logging_config import setup_logging, get_logger


def test_exceptions():
    """Test custom exception hierarchy."""
    print("\nExceptions:")

    # Project errors
    try:
        raise ProjectNotFoundError("test-123")
    except ProjectNotFoundError as e:
        assert "test-123" in str(e)
        assert e.details["project_id"] == "test-123"
        print("  ✓ ProjectNotFoundError")

    try:
        raise ProjectValidationError("name", "too long")
    except ProjectValidationError as e:
        assert "name" in str(e)
        assert e.details["field"] == "name"
        print("  ✓ ProjectValidationError")

    try:
        raise ProjectPersistenceError("save", "/path", "disk full")
    except ProjectPersistenceError as e:
        assert "save" in str(e)
        assert e.details["operation"] == "save"
        print("  ✓ ProjectPersistenceError")

    # Asset errors
    try:
        raise AssetNotFoundError("img-123")
    except AssetNotFoundError as e:
        assert "img-123" in str(e)
        print("  ✓ AssetNotFoundError")

    try:
        raise AssetValidationError("test.png", "too large")
    except AssetValidationError as e:
        assert "test.png" in str(e)
        print("  ✓ AssetValidationError")

    # Deployment errors
    try:
        raise DeploymentPlatformNotSupportedError("heroku", ["vercel", "netlify"])
    except DeploymentPlatformNotSupportedError as e:
        assert "heroku" in str(e)
        assert "vercel" in str(e)
        print("  ✓ DeploymentPlatformNotSupportedError")

    # Security errors
    try:
        raise PathTraversalError("../../etc/passwd")
    except PathTraversalError as e:
        assert "../../etc/passwd" in str(e)
        print("  ✓ PathTraversalError")

    try:
        raise InputSanitizationError("url", "invalid scheme")
    except InputSanitizationError as e:
        assert "url" in str(e)
        print("  ✓ InputSanitizationError")


def test_validation():
    """Test validation functions."""
    print("\nValidation:")

    # Valid project
    valid_project = {
        "id": "test-123",
        "name": "Test Project",
        "pages": [{"id": "p1", "name": "Home", "sections": []}],
        "design": {"colors": {"primary": "#3b82f6"}, "fonts": {"heading": "Inter"}},
    }
    errors = validate_project(valid_project)
    assert len(errors) == 0
    print("  ✓ Valid project passes")

    # Invalid project - missing required field
    invalid_project = {"name": "Test", "pages": []}
    errors = validate_project(invalid_project)
    assert len(errors) > 0
    print(f"  ✓ Invalid project caught: {errors[0]}")

    # Invalid project - bad ID format
    invalid_project2 = {
        "id": "test 123",  # spaces not allowed
        "name": "Test",
        "pages": [{"id": "p1", "name": "Home", "sections": []}],
        "design": {"colors": {}, "fonts": {}},
    }
    errors = validate_project(invalid_project2)
    assert any("id" in e.lower() for e in errors)
    print(f"  ✓ Bad ID format caught: {errors[0]}")

    # Invalid color
    invalid_color = {
        "id": "test",
        "name": "Test",
        "pages": [{"id": "p1", "name": "Home", "sections": []}],
        "design": {"colors": {"primary": "not-a-color"}, "fonts": {}},
    }
    errors = validate_project(invalid_color)
    assert any("color" in e.lower() for e in errors)
    print(f"  ✓ Invalid color caught: {errors[0]}")

    # Section type validation
    error = validate_section_type("Invalid Type")
    assert error is not None
    print(f"  ✓ Invalid section type caught: {error[:50]}...")

    error = validate_section_type("Hero — Centered")
    assert error is None
    print("  ✓ Valid section type passes")

    # Section props validation
    errors = validate_section_props("Hero — Centered", {"title": 123})
    assert len(errors) > 0
    print(f"  ✓ Invalid prop type caught: {errors[0]}")

    errors = validate_section_props("Hero — Centered", {"title": "Valid"})
    assert len(errors) == 0
    print("  ✓ Valid props pass")


def test_sanitization():
    """Test input sanitization."""
    print("\nSanitization:")

    # String sanitization
    result = sanitize_string("<script>alert('xss')</script>")
    assert "<script>" not in result
    assert "&lt;script&gt;" in result
    print("  ✓ String sanitization (XSS prevention)")

    result = sanitize_string("  hello  ")
    assert result == "hello"
    print("  ✓ String trimming")

    result = sanitize_string("a" * 20000, max_length=1000)
    assert len(result) == 1000
    print("  ✓ String length limiting")

    # Filename sanitization
    result = sanitize_filename("../../etc/passwd")
    assert ".." not in result
    assert "/" not in result
    print("  ✓ Filename path traversal prevention")

    result = sanitize_filename("my file (1).png")
    assert " " not in result
    print("  ✓ Filename special char removal")

    # Path sanitization
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        result = sanitize_path("subdir/file.txt", base)
        assert str(result).startswith(str(base))
        print("  ✓ Path sanitization (valid)")

        try:
            sanitize_path("../../etc/passwd", base)
            assert False, "Should have raised PathTraversalError"
        except PathTraversalError:
            print("  ✓ Path traversal detection")

    # URL sanitization
    result = sanitize_url("https://example.com")
    assert result == "https://example.com"
    print("  ✓ URL sanitization (https)")

    result = sanitize_url("http://example.com")
    assert result == "http://example.com"
    print("  ✓ URL sanitization (http)")

    result = sanitize_url("/relative/path")
    assert result == "/relative/path"
    print("  ✓ URL sanitization (relative)")

    result = sanitize_url("#anchor")
    assert result == "#anchor"
    print("  ✓ URL sanitization (anchor)")

    # Color sanitization
    result = sanitize_color("#3b82f6")
    assert result == "#3b82f6"
    print("  ✓ Color sanitization (hex)")

    result = sanitize_color("rgb(59, 130, 246)")
    assert result == "rgb(59, 130, 246)"
    print("  ✓ Color sanitization (rgb)")

    try:
        sanitize_color("not-a-color")
        assert False, "Should have raised InputSanitizationError"
    except InputSanitizationError:
        print("  ✓ Invalid color rejection")


def test_color_validation():
    """Test color validation."""
    print("\nColor Validation:")

    valid_colors = [
        "#3b82f6",
        "#fff",
        "#12345678",
        "rgb(59, 130, 246)",
        "rgba(59, 130, 246, 0.5)",
        "hsl(217, 91%, 60%)",
        "hsla(217, 91%, 60%, 0.5)",
        "red",
        "blue",
        "transparent",
        "inherit",
    ]
    for color in valid_colors:
        assert _is_valid_color(color), f"Should be valid: {color}"
    print(f"  ✓ {len(valid_colors)} valid colors accepted")

    invalid_colors = [
        "not-a-color",
        "#",
        "#12345",
        "rgb(999, 999, 999)",  # Values out of range
        "javascript:alert(1)",
        "",
    ]
    for color in invalid_colors:
        assert not _is_valid_color(color), f"Should be invalid: {color}"
    print(f"  ✓ {len(invalid_colors)} invalid colors rejected")


def test_logging():
    """Test logging setup."""
    print("\nLogging:")

    import logging

    # Test logger creation
    logger = get_logger("test")
    assert logger.name == "webbuilder.test"
    print("  ✓ Logger creation")

    # Test setup with custom directory
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir) / "logs"
        logger = setup_logging("test_app", log_dir=log_dir)
        assert log_dir.exists()
        print("  ✓ Log directory creation")

        # Test file handler
        logger.info("Test message")
        log_file = log_dir / "test_app.log"
        assert log_file.exists()
        print("  ✓ Log file creation")

        # Verify log content
        with open(log_file) as f:
            content = f.read()
        assert "Test message" in content
        print("  ✓ Log message written")

        # Close handlers to release file locks
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


def test_project_manager_with_validation():
    """Test ProjectManager with validation and error handling."""
    print("\nProjectManager:")

    with tempfile.TemporaryDirectory() as tmpdir:
        pm = ProjectManager(Path(tmpdir))

        # Create and save
        project = pm.create_new("Test Project")
        assert project.id in [p["id"] for p in pm.list_projects()]
        print("  ✓ Project creation")

        # Load
        loaded = pm.load(project.id)
        assert loaded.name == "Test Project"
        print("  ✓ Project loading")

        # Backup
        backup_path = pm.backup(project.id)
        assert backup_path.exists()
        print("  ✓ Project backup")

        # Delete
        assert pm.delete(project.id)
        print("  ✓ Project deletion")

        # Load non-existent
        try:
            pm.load("non-existent")
            assert False, "Should have raised ProjectNotFoundError"
        except ProjectNotFoundError as e:
            assert "non-existent" in str(e)
            print("  ✓ ProjectNotFoundError on missing project")

        # Delete non-existent
        try:
            pm.delete("non-existent")
            assert False, "Should have raised ProjectNotFoundError"
        except ProjectNotFoundError:
            print("  ✓ ProjectNotFoundError on delete missing")


def test_asset_validation():
    """Test asset validation."""
    print("\nAsset Validation:")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a valid PNG file
        png_path = Path(tmpdir) / "test.png"
        # Minimal PNG header
        with open(png_path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82")

        error = validate_image_file(png_path)
        assert error is None
        print("  ✓ Valid PNG accepted")

        # Invalid extension
        bad_path = Path(tmpdir) / "test.exe"
        bad_path.write_bytes(b"fake")
        error = validate_image_file(bad_path)
        assert error is not None
        print(f"  ✓ Bad extension rejected: {error[:40]}...")

        # Empty file
        empty_path = Path(tmpdir) / "empty.png"
        empty_path.write_bytes(b"")
        error = validate_image_file(empty_path)
        assert error is not None
        print(f"  ✓ Empty file rejected: {error[:40]}...")

        # File too large
        large_path = Path(tmpdir) / "large.png"
        large_path.write_bytes(b"\x89PNG" + b"\x00" * (11 * 1024 * 1024))  # 11MB
        error = validate_image_file(large_path)
        assert error is not None
        print(f"  ✓ Oversized file rejected: {error[:40]}...")


if __name__ == "__main__":
    print("=" * 60)
    print("WebBuilder Robustness Tests")
    print("=" * 60)

    tests = [
        ("Exceptions", test_exceptions),
        ("Validation", test_validation),
        ("Sanitization", test_sanitization),
        ("Color Validation", test_color_validation),
        ("Logging", test_logging),
        ("ProjectManager", test_project_manager_with_validation),
        ("Asset Validation", test_asset_validation),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"\n  ❌ {name} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    print(f"{'=' * 60}")

    if failed > 0:
        sys.exit(1)
