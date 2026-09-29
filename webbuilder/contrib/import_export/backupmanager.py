from __future__ import annotations
import shutil
import time
from pathlib import Path

from webbuilder.core import ProjectManager


class BackupManager:
    def __init__(self, backup_dir):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, project_manager: ProjectManager):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)
        storage_dir = project_manager.storage_dir
        for proj_file in storage_dir.glob("*.json"):
            shutil.copy2(proj_file, backup_path / proj_file.name)
        return backup_path

    def list_backups(self):
        return sorted(self.backup_dir.glob("backup_*"), key=lambda p: p.name, reverse=True)

    def backup(self, project, name=None):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_name = f"{name}_{timestamp}" if name else f"project_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        data = project.to_dict() if hasattr(project, "to_dict") else {"name": getattr(project, "name", "")}
        import json
        with open(backup_path / "project.json", "w") as f:
            json.dump(data, f, indent=2, default=str)
        return str(backup_path)

    def restore(self, backup_name, target=None):
        backup_path = self.backup_dir / backup_name
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_name}")
        target_path = Path(target) if target else self.backup_dir / f"restored_{backup_name}"
        if backup_path.is_dir():
            shutil.copytree(backup_path, target_path, dirs_exist_ok=True)
        else:
            shutil.copy2(backup_path, target_path)
        return str(target_path)
