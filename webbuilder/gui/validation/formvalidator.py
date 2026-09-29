"""webbuilder.gui.validation.formvalidator — Form validation class."""

from __future__ import annotations
from typing import Any, Callable


class FormValidator:
    """Validates form fields against per-field rule sets."""

    def __init__(self):
        self._fields: dict[str, list] = {}

    def add_rule(self, rule: Callable[[Any], tuple[bool, str]]):
        """Add a validation rule. Rule returns (is_valid, error_message)."""
        if "_default" not in self._fields:
            self._fields["_default"] = []
        self._fields["_default"].append(rule)

    def add_field(self, field_name: str, rules: list) -> None:
        """Add rules for a specific field."""
        self._fields[field_name] = rules

    def validate(self, value: Any) -> list[str]:
        """Return a list of error messages. Empty list means valid."""
        rules = self._fields.get("_default", [])
        errors: list[str] = []
        for rule in rules:
            ok, msg = rule(value)
            if not ok:
                errors.append(msg)
        return errors

    def validate_form(self, data: dict) -> tuple[bool, dict[str, str]]:
        """Validate all fields. Returns (is_valid, {field: error})."""
        errors: dict[str, str] = {}
        for field_name, rules in self._fields.items():
            if field_name == "_default":
                continue
            value = data.get(field_name, "")
            for rule in rules:
                if not rule.validate(str(value)):
                    errors[field_name] = rule.error_msg
                    break
        return len(errors) == 0, errors

    def is_valid(self, value: Any) -> bool:
        return len(self.validate(value)) == 0

    def clear(self):
        self._fields.clear()
