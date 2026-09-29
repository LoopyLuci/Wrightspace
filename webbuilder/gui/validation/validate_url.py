"""webbuilder.gui.validation.validate_url — URL validation function."""

from __future__ import annotations
import re


def validate_url(value: str) -> tuple[bool, str]:
    """Validate URL format. Empty is allowed.

    Returns (is_valid, error_message).
    """
    if not value:
        return True, ""
    if re.match(r'^https?://', str(value)):
        return True, ""
    return False, "Invalid URL format"
