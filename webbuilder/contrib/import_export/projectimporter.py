from __future__ import annotations
import json
import zipfile
from pathlib import Path

from webbuilder.core import Project, ProjectManager


class ProjectImporter:
    def __init__(self, project_manager: ProjectManager = None):
        self.project_manager = project_manager

    def import_from_json(self, data: dict) -> Project:
        return Project.from_dict(data)

    def import_from_zip(self, zip_path: Path) -> list:
        projects = []
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                if name.endswith(".json"):
                    data = json.loads(zf.read(name))
                    projects.append(Project.from_dict(data))
        return projects

    def import_project(self, path):
        with open(path) as f:
            data = json.load(f)
        return Project.from_dict(data)

    def import_string(self, data_str):
        data = json.loads(data_str)
        return Project.from_dict(data)
