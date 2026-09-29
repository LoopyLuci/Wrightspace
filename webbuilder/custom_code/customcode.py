from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class CustomCode:
    html: str = ""
    css: str = ""
    js: str = ""
    head_tags: str = ""
    footer_scripts: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "html": self.html,
            "css": self.css,
            "js": self.js,
            "head_tags": self.head_tags,
            "footer_scripts": self.footer_scripts,
        }
