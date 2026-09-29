"""webbuilder.gui.validation.validate_number — Numeric validation function."""

from __future__ import annotations
from typing import Optional


def validate_number(value: str, min_val: Optional[float] = None,
                    max_val: Optional[float] = None) -> tuple[bool, str]:
    """Validate that a value is a number within optional bounds.

    Returns (is_valid, error_message).
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        return False, "Not a valid number"
    if min_val is not None and num < min_val:
        return False, f"Value must be at least {min_val}"
    if max_val is not None and num > max_val:
        return False, f"Value must be at most {max_val}"
    return True, ""
