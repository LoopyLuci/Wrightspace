from __future__ import annotations
import re
from typing import Dict, List, Optional

from webbuilder.custom_code.customcode import CustomCode

_DANGEROUS_PATTERNS = [
    re.compile(r'<\s*script[\s>]', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),
    re.compile(r'javascript\s*:', re.IGNORECASE),
]


class CustomCodeManager:
    def __init__(self):
        self._snippets: Dict[str, CustomCode] = {}

    def set(self, project_id: str, code: CustomCode) -> List[str]:
        errors: List[str] = []
        if not project_id:
            errors.append("Project ID is required")
        if not isinstance(code, CustomCode):
            errors.append("Code must be a CustomCode instance")
        if not errors:
            for field_name in ('html', 'css', 'js', 'head_tags', 'footer_scripts'):
                value = getattr(code, field_name, '')
                if not isinstance(value, str):
                    continue
                for pattern in _DANGEROUS_PATTERNS:
                    if pattern.search(value):
                        errors.append(f"Dangerous pattern detected in {field_name}")
                        break
        if not errors:
            self._snippets[project_id] = code
        return errors

    def get(self, project_id: str) -> Optional[CustomCode]:
        return self._snippets.get(project_id)

    def delete(self, project_id: str) -> bool:
        return self._snippets.pop(project_id, None) is not None

    def export_code(self, project_id: str) -> dict:
        code = self.get(project_id)
        if code is None:
            return {}
        return code.to_dict()
