"""webbuilder.core.sqlite_backend.sqliteprojectbackend — SQLite project storage."""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from webbuilder.core import Project


class SQLiteProjectBackend:
    """SQLite-backed storage for WebBuilder projects."""

    def __init__(self, db_path: Union[str, Path] = ":memory:"):
        self.db_path = str(db_path)
        self._conn: Optional[sqlite3.Connection] = None
        self._connect()

    def _connect(self):
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._ensure_tables()

    def _ensure_tables(self):
        if not self._conn:
            return
        cur = self._conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY, name TEXT, description TEXT,
            data TEXT, created TEXT, updated TEXT)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS pages (
            id TEXT PRIMARY KEY, project_id TEXT, name TEXT, data TEXT)""")
        self._conn.commit()

    def save_project(self, project: Any) -> str:
        if not self._conn:
            return ""
        data = project.to_dict() if hasattr(project, "to_dict") else {"name": project.name}
        cur = self._conn.cursor()
        cur.execute("INSERT OR REPLACE INTO projects (id, name, description, data, created, updated) VALUES (?, ?, ?, ?, ?, ?)",
            (project.id, project.name, getattr(project, "description", ""), json.dumps(data, default=str), getattr(project, "created_at", ""), datetime.now().isoformat()))
        self._conn.commit()
        return project.id

    def load_project(self, project_id: str) -> Optional[Project]:
        if not self._conn:
            return None
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cur.fetchone()
        if row is None:
            return None
        data = json.loads(row["data"]) if row["data"] else {}
        return Project.from_dict({**data, "id": row["id"], "name": row["name"]})

    def list_projects(self) -> List[Project]:
        if not self._conn:
            return []
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM projects")
        results = []
        for row in cur.fetchall():
            data = json.loads(row["data"]) if row["data"] else {}
            results.append(Project.from_dict({**data, "id": row["id"], "name": row["name"]}))
        return results

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
