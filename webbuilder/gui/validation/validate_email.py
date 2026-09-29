"""webbuilder.gui.validation.validate_email — Email validation function."""

from __future__ import annotations
import re


def validate_email(value: str) -> tuple[bool, str]:
    """Validate email format. Empty is allowed.

    Returns (is_valid, error_message).
    """
    if not value:
        return True, ""
    if re.match(r'^[^@]+@[^@]+\.[^@]+$', str(value)):
        return True, ""
    return False, "Invalid email format"
