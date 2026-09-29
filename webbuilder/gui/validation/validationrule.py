"""webbuilder.gui.validation.validationrule — Individual validation rule."""

from __future__ import annotations
from typing import Callable, Any


class ValidationRule:
    """A single validation rule with a name, validator function, and error message."""

    def __init__(self, name: str, validator: Callable[[Any], bool], error_msg: str):
        self.name = name
        self.validator = validator
        self.error_msg = error_msg

    def validate(self, value: Any) -> bool:
        return self.validator(value)

    def __call__(self, value: Any) -> bool:
        return self.validate(value)
