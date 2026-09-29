"""webbuilder.export.reactexporter — Export project to React components."""

from __future__ import annotations
from typing import Any


class ReactExporter:
    """Exports a WebBuilder project to a React component file."""

    def generate(self, project: Any) -> str:
        lines: list[str] = []
        lines.append("import React from 'react';")
        lines.append("")
        lines.append("const WebBuilderApp = () => {")
        lines.append("  return (")
        lines.append("    <div className='webbuilder-app'>")
        lines.append(f"      <h1>{project.name or 'WebBuilder Project'}</h1>")
        for page in getattr(project, "pages", []):
            lines.append(f"      <section id='page-{page.id}'>")
            lines.append(f"        <h2>{page.name or 'Untitled'}</h2>")
            lines.append("      </section>")
        lines.append("    </div>")
        lines.append("  );")
        lines.append("};")
        lines.append("")
        lines.append("export default WebBuilderApp;")
        return "\n".join(lines)

    def export(self, project: Any, output_path: str) -> str:
        """Export a project to a React JSX file.

        Args:
            project: Project instance to export.
            output_path: Destination file path.

        Returns:
            The path to the exported file.
        """
        lines: list[str] = []
        lines.append("import React from 'react';")
        lines.append("")
        lines.append("const WebBuilderApp = () => {")
        lines.append("  return (")
        lines.append("    <div className='webbuilder-app'>")
        lines.append(f"      <h1>{project.name or 'WebBuilder Project'}</h1>")

        for page in getattr(project, "pages", []):
            lines.append(f"      <section id='page-{page.id}'>")
            lines.append(f"        <h2>{page.name or 'Untitled'}</h2>")
            lines.append("      </section>")

        lines.append("    </div>")
        lines.append("  );")
        lines.append("};")
        lines.append("")
        lines.append("export default WebBuilderApp;")

        content = self.generate(project)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path
