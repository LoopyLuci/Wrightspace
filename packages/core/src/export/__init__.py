"""packages.core.export — Export backends.

Provides export classes compatible with the core test suite.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional


class ProjectSchema:
    VERSION = "2.0.0"

    @staticmethod
    def validate(project: dict) -> bool:
        required = ['id', 'name', 'pages', 'design']
        return all(k in project for k in required)

    @staticmethod
    def migrate(project: dict) -> dict:
        version = project.get('version', '1.0.0')
        if version == '1.0.0':
            project['design'] = {
                'colors': project.get('colors', {}),
                'fonts': project.get('fonts', {'heading': 'Inter', 'body': 'Inter'})
            }
            project.pop('colors', None)
            project.pop('fonts', None)
            project['version'] = '2.0.0'
        return project


class HTMLExporter:
    def __init__(self, project: dict):
        self.project = project
        self.design = project.get('design', {})
        self.colors = self.design.get('colors', {})
        self.fonts = self.design.get('fonts', {'heading': 'Inter', 'body': 'Inter'})
        self.name = project.get('name', 'Project')

    def generate_html(self) -> str:
        parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            f'<meta charset="UTF-8">',
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'<title>{self.name}</title>',
            '<style>',
            f'body {{ font-family: {self.fonts.get("body", "Inter")}, sans-serif; margin: 0; padding: 0; }}',
            f'h1, h2 {{ font-family: {self.fonts.get("heading", "Inter")}, sans-serif; }}',
            '.hero { padding: 4rem 2rem; text-align: center; }',
            '.features { padding: 3rem 2rem; }',
            '.footer { padding: 2rem; text-align: center; background: #f5f5f5; }',
            '</style>',
            '</head>',
            '<body>',
        ]
        for page in self.project.get('pages', []):
            for section in page.get('sections', []):
                parts.append(self.render_section(section))
        parts.extend(['</body>', '</html>'])
        return '\n'.join(parts)

    def render_section(self, section: dict) -> str:
        stype = section.get('type', '')
        props = section.get('props', {})
        title = props.get('title', '')
        subtitle = props.get('subtitle', '')
        cta = props.get('ctaText', '')
        copyright_text = props.get('copyright', '')
        bg = props.get('backgroundColor', '')
        items = props.get('items', [])
        tiers = props.get('tiers', [])
        links = props.get('links', [])

        if 'hero' in stype:
            style = f' style="background-color:{bg}"' if bg else ''
            html = f'<div class="hero"{style}><h1>{title}</h1>'
            if subtitle:
                html += f'<p>{subtitle}</p>'
            if cta:
                html += f'<a href="#" class="cta">{cta}</a>'
            html += '</div>'
            return html

        if 'features' in stype:
            html = f'<div class="features"><h2>{title}</h2>'
            if subtitle:
                html += f'<p>{subtitle}</p>'
            html += '<div class="feature-grid">'
            for item in items:
                html += f'<div class="feature"><h3>{item.get("title", "")}</h3><p>{item.get("description", "")}</p></div>'
            html += '</div></div>'
            return html

        if 'pricing' in stype:
            html = f'<div class="pricing"><h2>{title}</h2><div class="pricing-grid">'
            for tier in tiers:
                html += f'<div class="tier"><h3>{tier.get("name", "")}</h3><div class="price">{tier.get("price", "")}</div><ul>'
                for f in tier.get('features', []):
                    html += f'<li>{f}</li>'
                html += '</ul></div>'
            html += '</div></div>'
            return html

        if 'footer' in stype:
            html = '<footer class="footer">'
            if copyright_text:
                html += f'<p>{copyright_text}</p>'
            if links:
                html += '<ul>' + ''.join(f'<li>{l}</li>' for l in links) + '</ul>'
            html += '</footer>'
            return html

        html = f'<div class="{stype}">'
        if title:
            html += f'<h2>{title}</h2>'
        if subtitle:
            html += f'<p>{subtitle}</p>'
        html += '</div>'
        return html

    def export(self, output_path: str) -> str:
        html = self.generate_html()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(html, encoding='utf-8')
        return output_path


class ReactExporter:
    def __init__(self, project: dict):
        self.project = project
        self.name = project.get('name', 'Project')

    def generate(self, project=None) -> str:
        p = project or self.project
        return self._generate_app(p)

    def _generate_app(self, project: dict) -> str:
        sections = []
        for page in project.get('pages', []):
            for section in page.get('sections', []):
                stype = section.get('type', 'div').replace('-', '')
                sections.append(f'    <{stype} />')
        return (
            'import React from "react";\n\n'
            f'export default function App() {{\n'
            f'  return (\n'
            f'    <div className="app">\n'
            f'{chr(10).join(sections)}\n'
            f'    </div>\n'
            f'  );\n'
            f'}}\n'
        )

    def export(self, output_dir: str) -> str:
        out = Path(output_dir)
        (out / 'src').mkdir(parents=True, exist_ok=True)
        (out / 'src' / 'App.jsx').write_text(self._generate_app(self.project), encoding='utf-8')
        (out / 'src' / 'index.jsx').write_text(
            'import React from "react";\nimport ReactDOM from "react-dom";\nimport App from "./App";\nReactDOM.render(<App />, document.getElementById("root"));\n',
            encoding='utf-8')
        (out / 'src' / 'styles.css').write_text('/* styles */\n', encoding='utf-8')
        (out / 'package.json').write_text(json.dumps({
            'name': self.name.lower().replace(' ', '-'),
            'version': '1.0.0',
            'dependencies': {'react': '^18.0.0', 'react-dom': '^18.0.0'},
            'scripts': {'start': 'react-scripts start', 'build': 'react-scripts build'}
        }, indent=2), encoding='utf-8')
        return str(out)


class VueExporter:
    def __init__(self, project: dict):
        self.project = project

    def generate(self, project=None) -> str:
        p = project or self.project
        name = p.get('name', 'App')
        return (
            f'<template>\n  <div id="app">\n'
            + ''.join(f'    <{s.get("type", "div")} />\n' for page in p.get('pages', []) for s in page.get('sections', []))
            + '  </div>\n</template>\n\n<script>\nexport default { name: "App" };\n</script>\n'
        )

    def export(self, output_path: str) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(self.generate(), encoding='utf-8')
        return output_path


class JSONExporter:
    def __init__(self, project: dict):
        self.project = project

    def generate(self, project=None) -> str:
        return json.dumps({
            'version': ProjectSchema.VERSION,
            'exported_at': datetime.now().isoformat(),
            'project': project or self.project
        }, indent=2)

    def export(self, output_path: str) -> str:
        data = {
            'version': ProjectSchema.VERSION,
            'exported_at': datetime.now().isoformat(),
            'project': self.project
        }
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(data, indent=2), encoding='utf-8')
        return output_path


class ExportManager:
    _FORMATS = {'html': HTMLExporter, 'react': ReactExporter, 'json': JSONExporter, 'vue': VueExporter}

    def __init__(self, project: dict):
        self.project = project

    def export(self, format_name: str, output_path: str) -> str:
        if format_name not in self._FORMATS:
            raise ValueError(f"Unknown format: {format_name}. Available: {list(self._FORMATS.keys())}")
        exporter = self._FORMATS[format_name](self.project)
        if format_name == 'react':
            return exporter.export(output_path)
        return exporter.export(output_path)

    def export_all(self, output_dir: str) -> dict:
        results = {}
        for fmt, cls in self._FORMATS.items():
            exp = cls(self.project)
            path = os.path.join(output_dir, fmt)
            if fmt == 'react':
                results[fmt] = exp.export(path)
            else:
                ext = '.html' if fmt == 'html' else f'.{fmt}'
                results[fmt] = exp.export(path + ext)
        return results


__all__ = [
    "ProjectSchema", "HTMLExporter", "ReactExporter", "VueExporter",
    "JSONExporter", "ExportManager",
]
