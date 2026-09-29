from __future__ import annotations
from typing import Any, Dict, List, Optional

from webbuilder.templates.template import Template


class TemplateManager:

    def __init__(self):
        self.templates: Dict[str, Template] = {}
        self._load_builtin_templates()

    def _load_builtin_templates(self):
        self.templates["saas-landing"] = Template(
            id="saas-landing",
            name="SaaS Landing Page",
            description="Modern SaaS product landing page",
            category="Business",
        )
        self.templates["portfolio"] = Template(
            id="portfolio",
            name="Creative Portfolio",
            description="Showcase your work",
            category="Portfolio",
        )
        self.templates["blog"] = Template(
            id="blog",
            name="Blog Template",
            description="Minimal blog layout",
            category="Business",
        )
        self.templates["ecommerce"] = Template(
            id="ecommerce",
            name="E-Commerce Store",
            description="Online store template",
            category="Business",
        )

    def get_all_templates(self) -> List[Template]:
        return list(self.templates.values())

    def get_categories(self) -> List[str]:
        return list({t.category for t in self.templates.values()})

    def get_template(self, template_id: str) -> Optional[Template]:
        return self.templates.get(template_id)

    def search_templates(self, query: str) -> List[Template]:
        q = query.lower()
        return [
            t
            for t in self.templates.values()
            if q in t.name.lower() or q in t.description.lower()
        ]

    def get_templates_by_category(self, category: str) -> List[Template]:
        return [t for t in self.templates.values() if t.category == category]

    def create_project_from_template(
        self, template_id: str, project_id: str, project_name: str
    ) -> Optional[Dict[str, Any]]:
        template = self.templates.get(template_id)
        if not template:
            return None
        return {"project_id": project_id, "name": project_name, "template_id": template_id}
