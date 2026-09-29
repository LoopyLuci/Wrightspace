"""webbuilder.templates.template — Template data model."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json


@dataclass
class Template:
    """A page template definition.

    Attributes:
        id: Unique template identifier.
        name: Human-readable name.
        description: Template description.
        html: HTML template string with placeholders.
        css: CSS styles for the template.
        js: JavaScript for the template.
        category: Template category (landing, blog, portfolio, etc.).
        thumbnail: Path to thumbnail image.
        components: List of supported component types.
        variables: Template variables that can be customized.
    """

    id: str = ""
    name: str = ""
    description: str = ""
    html: str = ""
    css: str = ""
    js: str = ""
    category: str = "general"
    thumbnail: str = ""
    components: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize template to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "html": self.html,
            "css": self.css,
            "js": self.js,
            "category": self.category,
            "thumbnail": self.thumbnail,
            "components": self.components,
            "variables": self.variables,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Template":
        """Create a template from a dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            html=data.get("html", ""),
            css=data.get("css", ""),
            js=data.get("js", ""),
            category=data.get("category", "general"),
            thumbnail=data.get("thumbnail", ""),
            components=data.get("components", []),
            variables=data.get("variables", {}),
        )

    def render(self, context: Dict[str, Any]) -> str:
        """Render the template with the given context.

        Values are HTML-escaped to prevent injection.
        """
        import html as html_mod
        result = self.html
        for key, value in context.items():
            result = result.replace("{{" + key + "}}", html_mod.escape(str(value)))
        return result
