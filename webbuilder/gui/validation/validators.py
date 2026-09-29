"""webbuilder.gui.validation.validators — Validation utility functions for forms."""

from __future__ import annotations
import re
from typing import Any, Callable, Optional


class Validators:
    """Convenience class providing static validation methods."""

    @staticmethod
    def required(value: str) -> bool:
        return bool(value and str(value).strip())

    @staticmethod
    def email(value: str) -> bool:
        if not value:
            return True
        return bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', str(value)))

    @staticmethod
    def url(value: str) -> bool:
        if not value:
            return True
        return bool(re.match(r'^https?://', str(value)))

    @staticmethod
    def hex_color(value: str) -> bool:
        if not value:
            return True
        return bool(re.match(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$', value))

    @staticmethod
    def number(value: Any) -> bool:
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                return False
        return False

    @staticmethod
    def project_name(value: str) -> bool:
        if not isinstance(value, str):
            return False
        value = value.strip()
        if not value:
            return False
        if len(value) > 100:
            return False
        return True

    @staticmethod
    def min_length(n: int) -> Callable[[str], bool]:
        def validator(value: str) -> bool:
            return len(str(value)) >= n
        return validator

    @staticmethod
    def range(min_val: float, max_val: float) -> Callable[[str], bool]:
        def validator(value: str) -> bool:
            try:
                num = float(value)
            except (ValueError, TypeError):
                return False
            return min_val <= num <= max_val
        return validator
