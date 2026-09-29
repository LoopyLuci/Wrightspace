"""webbuilder.gui.validation.validate_project_name — Project name validation."""

from __future__ import annotations


def validate_project_name(value: str) -> tuple[bool, str]:
    """Validate a project name.

    Returns (is_valid, error_message).
    """
    if not isinstance(value, str):
        return False, "Project name is required"
    if not value.strip():
        return False, "Project name is required"
    if len(value) > 100:
        return False, "Project name too long (max 100 characters)"
    return True, ""
