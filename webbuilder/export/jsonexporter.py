"""webbuilder.export.jsonexporter — Export project to JSON."""

from __future__ import annotations
from typing import Any
import json


class JSONExporter:
    """Exports a WebBuilder project to a JSON file."""

    def generate(self, project: Any) -> str:
        if hasattr(project, "to_dict"):
            data = project.to_dict()
        else:
            data = {"name": getattr(project, "name", str(project))}
        return json.dumps(data, indent=2, ensure_ascii=False)

    def export(self, project: Any, output_path: str) -> str:
        """Export a project to a JSON file.

        Args:
            project: Project instance to export.
            output_path: Destination file path.

        Returns:
            The path to the exported JSON file.
        """
        content = self.generate(project)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path
