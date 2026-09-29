from __future__ import annotations
import json
from pathlib import Path

from webbuilder.core import Project, ProjectManager


class ProjectExporter:
    def __init__(self, project_manager: ProjectManager = None):
        self.project_manager = project_manager

    def export_to_json(self, project_id: str, output_path: Path) -> Path:
        pm = self.project_manager
        if pm:
            project = pm.load(project_id)
        else:
            return output_path
        if project:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(project.to_dict(), indent=2))
        return output_path

    def export_to_zip(self, project_ids: list, output_path: Path) -> Path:
        import zipfile
        pm = self.project_manager
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for pid in project_ids:
                if pm:
                    project = pm.load(pid)
                    if project:
                        zf.writestr(f"{pid}.json", json.dumps(project.to_dict(), indent=2))
        return output_path

    def export(self, project, output_path):
        return self.export_to_json(project.id, Path(output_path))

    def export_string(self, project):
        return json.dumps(project.to_dict(), indent=2, default=str)
