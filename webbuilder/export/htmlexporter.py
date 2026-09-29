"""webbuilder.export.htmlexporter — Export project to standalone HTML."""

from __future__ import annotations
from typing import Any
import json
import html

from webbuilder.core import Page, Section, Project


class HTMLExporter:
    """Exports a WebBuilder project to a single HTML file."""

    def __init__(self):
        self.indent = "  "

    def _ensure_object(self, project: Any) -> Project:
        if isinstance(project, dict):
            return Project.from_dict(project)
        return project

    def generate(self, project: Any) -> str:
        project = self._ensure_object(project)
        html_parts: list[str] = []
        html_parts.append("<!DOCTYPE html>")
        html_parts.append('<html lang="en">')
        html_parts.append("<head>")
        html_parts.append('<meta charset="UTF-8">')
        html_parts.append(f'<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_parts.append(f"<title>{html.escape(project.name or 'WebBuilder Project')}</title>")
        html_parts.append("<style>")
        html_parts.append("  * { margin: 0; padding: 0; box-sizing: border-box; }")
        html_parts.append("  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 2rem; background: #f8fafc; color: #1e293b; }")
        html_parts.append("  h1 { font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; color: #0f172a; }")
        html_parts.append("  h2 { font-size: 1.5rem; font-weight: 600; margin-bottom: 0.75rem; color: #334155; }")
        html_parts.append("  section { margin-bottom: 2rem; }")
        html_parts.append("  .section { padding: 1.5rem; margin-bottom: 1rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }")
        html_parts.append("  .item { padding: 0.5rem 0; color: #475569; }")
        html_parts.append("  .copyright { padding: 0.5rem 0; color: #64748b; font-size: 0.875rem; }")
        html_parts.append("  @media (max-width: 768px) { body { padding: 1rem; } }")
        html_parts.append("</style>")
        html_parts.append("</head>")
        html_parts.append("<body>")
        html_parts.append(f"<h1>{html.escape(project.name or 'WebBuilder Project')}</h1>")
        html_parts.append(f'<div id="app">')
        for page in project.pages:
            html_parts.append(f'<section id="page-{page.id}">')
            html_parts.append(f"  <h2>{html.escape(page.name or 'Untitled Page')}</h2>")
            for section in page.sections:
                html_parts.append(f'  <div class="section {html.escape(section.type or "default")}">')
                if section.props:
                    for key, value in section.props.items():
                        if isinstance(value, str):
                            html_parts.append(f'    <div class="{html.escape(str(key))}">{html.escape(value)}</div>')
                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    parts = [f'{k}: {v}' for k, v in item.items() if isinstance(v, str)]
                                    html_parts.append(f'    <div class="item">{html.escape(", ".join(parts))}</div>')
                                else:
                                    html_parts.append(f'    <div class="item">{html.escape(str(item))}</div>')
                html_parts.append("  </div>")
            html_parts.append("</section>")
        html_parts.append("</div>")
        html_parts.append("</body>")
        html_parts.append("</html>")
        return "\n".join(html_parts)

    def export(self, project: Any, output_path: str) -> str:
        """Export a project to an HTML file."""
        project = self._ensure_object(project)
        html_parts: list[str] = []

        html_parts.append("<!DOCTYPE html>")
        html_parts.append('<html lang="en">')
        html_parts.append("<head>")
        html_parts.append(f'<meta charset="UTF-8">')
        html_parts.append(f"<title>{html.escape(project.name or 'WebBuilder Project')}</title>")
        html_parts.append("</head>")
        html_parts.append("<body>")
        html_parts.append(f"<h1>{html.escape(project.name or 'WebBuilder Project')}</h1>")

        for page in project.pages:
            html_parts.append(f"<section id=\"page-{page.id}\">")
            html_parts.append(f"  <h2>{html.escape(page.name or 'Untitled Page')}</h2>")
            for section in page.sections:
                html_parts.append(f"  <div class=\"section {html.escape(section.type or 'default')}\">")
                if section.props:
                    for key, value in section.props.items():
                        if isinstance(value, str):
                            html_parts.append(f'    <div class="{html.escape(str(key))}">{html.escape(value)}</div>')
                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    parts = [f'{k}: {v}' for k, v in item.items() if isinstance(v, str)]
                                    html_parts.append(f'    <div class="item">{html.escape(", ".join(parts))}</div>')
                                else:
                                    html_parts.append(f'    <div class="item">{html.escape(str(item))}</div>')
                html_parts.append("  </div>")
            html_parts.append("</section>")

        html_parts.append("</body>")
        html_parts.append("</html>")

        content = self.generate(project)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path
