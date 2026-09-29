"""webbuilder.forms.formbuilder — Builds form UI from field definitions."""

from __future__ import annotations
import html
import re
import uuid
from typing import Any, Dict, List

from webbuilder.forms.formfield import FormField


class Form:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.id: str = uuid.uuid4().hex[:8]
        self.fields: List[FormField] = []


class FormBuilder:
    def __init__(self) -> None:
        self._forms: Dict[str, Form] = {}
        self._submissions: Dict[str, List[Dict[str, Any]]] = {}

    def create_form(self, name: str) -> Form:
        form = Form(name)
        self._forms[form.id] = form
        return form

    def add_field(
        self,
        form_id: str,
        field_type: str,
        label: str,
        required: bool = False,
        options: List[str] | None = None,
    ) -> FormField:
        form = self._forms[form_id]
        field = FormField(label=label, field_type=field_type, required=required, options=options)
        form.fields.append(field)
        return field

    def validate_submission(self, form_id: str, data: Dict[str, Any]) -> List[str]:
        form = self._forms[form_id]
        errors: List[str] = []
        for field in form.fields:
            value = data.get(field.id, "")
            if field.required and (value is None or str(value).strip() == ""):
                errors.append(f"{field.label} is required")
            if field.type == "email" and value and not self._is_valid_email(str(value)):
                errors.append(f"{field.label} is not a valid email")
        return errors

    def submit_form(self, form_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        errors = self.validate_submission(form_id, data)
        if len(errors) == 0:
            sanitized = {}
            for k, v in data.items():
                if isinstance(v, str):
                    import html as html_mod
                    sanitized[k] = html_mod.escape(v)
                else:
                    sanitized[k] = v
            if form_id not in self._submissions:
                self._submissions[form_id] = []
            self._submissions[form_id].append({"data": sanitized})
            return {"success": True, "data": sanitized}
        return {"success": False, "errors": errors}

    def get_submissions(self, form_id: str) -> List[Dict[str, Any]]:
        return self._submissions.get(form_id, [])

    def to_html(self, form: Form) -> str:
        lines: List[str] = []
        lines.append('<form class="webbuilder-form">')
        for field in form.fields:
            required_attr = " required" if field.required else ""
            label_text = html.escape(field.label)
            lines.append('  <div class="form-field">')
            lines.append(f'    <label for="{field.id}">{label_text}</label>')
            if field.type == "select":
                lines.append(f'    <select id="{field.id}" name="{field.id}">')
                for opt in field.options:
                    lines.append(f'      <option value="{html.escape(opt)}">{html.escape(opt)}</option>')
                lines.append("    </select>")
            else:
                lines.append(f'    <input type="{field.type}" id="{field.id}" name="{field.id}"{required_attr} />')
            lines.append("  </div>")
        lines.append('  <button type="submit">Submit</button>')
        lines.append("</form>")
        return "\n".join(lines)

    @staticmethod
    def _is_valid_email(value: str) -> bool:
        return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value))
