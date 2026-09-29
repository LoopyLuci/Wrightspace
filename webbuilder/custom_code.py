"""webbuilder.custom_code — Custom Code."""

import re
from dataclasses import dataclass, field


@dataclass
class CustomCode:
    """CustomCode — holds custom code snippets for a project."""
    html: str = ""
    css: str = ""
    js: str = ""
    head_tags: str = ""
    footer_scripts: str = ""


_DANGEROUS_HTML_PATTERNS = [
    re.compile(r'<\s*script[\s>]', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),
    re.compile(r'javascript\s*:', re.IGNORECASE),
]


class CustomCodeManager:
    """CustomCodeManager — validates and stores custom code."""

    def set(self, project_id: str, code: CustomCode) -> list[str]:
        errors = []
        for field_name in ('html', 'css', 'js', 'head_tags', 'footer_scripts'):
            value = getattr(code, field_name, '')
            if not isinstance(value, str):
                continue
            for pattern in _DANGEROUS_HTML_PATTERNS:
                if pattern.search(value):
                    errors.append(f"Dangerous pattern detected in {field_name}")
                    break
        return errors
