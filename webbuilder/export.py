"""webbuilder.export — auto-generated implementation."""

from __future__ import annotations

class ExportManager:
    """ExportManager."""

    def __init__(self):

        self._exporters = {}

    def register(self, fmt, exporter):

        self._exporters[fmt] = exporter

    def get_supported_formats(self):

        return list(self._exporters.keys())

    def export(self, project, fmt, output_dir):

        if fmt not in self._exporters:

            raise ValueError(f'Unknown export format: {fmt}')

        exporter = self._exporters[fmt]

        result = exporter.generate(project)

        import pathlib

        out = pathlib.Path(output_dir) / f'{project.id}.{fmt}'

        out.write_text(result)

        return out

    pass

class HTMLExporter():
    """HTMLExporter."""

    def generate(self, project):
        import html as _html
        safe_name = _html.escape(project.name)
        pages_html = []
        for page in project.pages:
            sections_html = []
            for section in page.sections:
                props_html = []
                for key, value in section.props.items():
                    safe_key = _html.escape(str(key))
                    safe_value = _html.escape(str(value))
                    props_html.append(f'<div data-prop="{safe_key}">{safe_value}</div>')
                sections_html.append(
                    f'<section data-type="{_html.escape(section.type)}">'
                    + ''.join(props_html)
                    + '</section>'
                )
            pages_html.append(
                f'<div data-page="{_html.escape(page.name)}">'
                + ''.join(sections_html)
                + '</div>'
            )
        return (
            '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
            f'<title>{safe_name}</title>\n'
            '</head>\n<body>\n'
            + ''.join(pages_html)
            + '\n</body>\n</html>'
        )

class JSONExporter():
    """JSONExporter."""
    pass

class ReactExporter():
    """ReactExporter."""
    pass

class VueExporter():
    """VueExporter."""
    pass


__all__ = ['ExportManager', 'HTMLExporter', 'JSONExporter', 'ReactExporter', 'VueExporter']
