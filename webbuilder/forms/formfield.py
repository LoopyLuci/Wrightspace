"""webbuilder.forms.formfield — Represents a single form field."""

from __future__ import annotations
import uuid
from typing import Any, Dict, List


class FormField:
    def __init__(
        self,
        label: str = "",
        field_type: str = "text",
        required: bool = False,
        options: List[str] | None = None,
    ) -> None:
        self.id: str = uuid.uuid4().hex[:8]
        self.label: str = label
        self.type: str = field_type
        self.required: bool = required
        self.options: List[str] = options if options is not None else []
