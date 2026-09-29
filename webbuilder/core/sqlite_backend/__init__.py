"""webbuilder.core.sqlite_backend — SQLite-backed project storage."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Optional


class SQLiteProjectBackend:
    """SQLite-backed project storage."""

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or Path("webbuilder.db")
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        cur = self._conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                data TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS search_index (
                project_id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            )
        """)
        self._conn.commit()

    def save_project(self, project_id: str, name: str, data: dict) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO projects (project_id, name, data) VALUES (?, ?, ?)",
            (project_id, name, json.dumps(data)),
        )
        self._conn.commit()

    def load_project(self, project_id: str) -> Optional[dict]:
        cur = self._conn.cursor()
        cur.execute("SELECT data FROM projects WHERE project_id = ?", (project_id,))
        row = cur.fetchone()
        if row is None:
            return None
        return json.loads(row["data"])

    def list_projects(self) -> list[dict]:
        cur = self._conn.cursor()
        cur.execute("SELECT project_id, name FROM projects")
        return [{"id": row["project_id"], "name": row["name"]} for row in cur.fetchall()]

    def delete_project(self, project_id: str) -> None:
        cur = self._conn.cursor()
        cur.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
        cur.execute("DELETE FROM search_index WHERE project_id = ?", (project_id,))
        self._conn.commit()

    def update_search_index(self, project_id: str, index_data: dict) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO search_index (project_id, data) VALUES (?, ?)",
            (project_id, json.dumps(index_data)),
        )
        self._conn.commit()

    def search(self, query: str) -> list[dict]:
        cur = self._conn.cursor()
        cur.execute("SELECT project_id, data FROM search_index")
        results = []
        for row in cur.fetchall():
            data = json.loads(row["data"])
            if any(query.lower() in str(v).lower() for v in data.values()):
                results.append({"id": row["project_id"], "data": data})
        return results

    def close(self) -> None:
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
