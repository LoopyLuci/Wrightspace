"""webbuilder.export.vueexporter — Export project to Vue components."""

from __future__ import annotations
from typing import Any


class VueExporter:
    """Exports a WebBuilder project to a Vue SFC."""

    def generate(self, project: Any) -> str:
        lines: list[str] = []
        lines.append("<template>")
        lines.append("  <div class='webbuilder-app'>")
        lines.append(f"    <h1>{project.name or 'WebBuilder Project'}</h1>")
        for page in getattr(project, "pages", []):
            lines.append(f"    <section id='page-{page.id}'>")
            lines.append(f"      <h2>{page.name or 'Untitled'}</h2>")
            lines.append("    </section>")
        lines.append("  </div>")
        lines.append("</template>")
        lines.append("")
        lines.append("<script>")
        lines.append("export default {")
        lines.append("  name: 'WebBuilderApp',")
        lines.append("  data() {")
        lines.append("    return {")
        lines.append("      projectName: '" + (project.name or 'WebBuilder Project') + "',")
        lines.append("    };")
        lines.append("  },")
        lines.append("};")
        lines.append("</script>")
        return "\n".join(lines)

    def export(self, project: Any, output_path: str) -> str:
        """Export a project to a Vue component file.

        Args:
            project: Project instance to export.
            output_path: Destination file path.

        Returns:
            The path to the exported file.
        """
        lines: list[str] = []
        lines.append("<template>")
        lines.append("  <div class='webbuilder-app'>")
        lines.append(f"    <h1>{project.name or 'WebBuilder Project'}</h1>")

        for page in getattr(project, "pages", []):
            lines.append(f"    <section id='page-{page.id}'>")
            lines.append(f"      <h2>{page.name or 'Untitled'}</h2>")
            lines.append("    </section>")

        lines.append("  </div>")
        lines.append("</template>")
        lines.append("")
        lines.append("<script>")
        lines.append("export default {")
        lines.append("  name: 'WebBuilderApp',")
        lines.append("  data() {")
        lines.append("    return {")
        lines.append("      projectName: '" + (project.name or 'WebBuilder Project') + "',")
        lines.append("    };")
        lines.append("  },")
        lines.append("};")
        lines.append("</script>")

        content = self.generate(project)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path
