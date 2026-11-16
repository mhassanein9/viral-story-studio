"""SQLite persistence. Each project is one row: indexed columns for listing, JSON for the full document."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from core.models import Project, utcnow


class ProjectRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    title      TEXT NOT NULL,
                    stage      TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload    TEXT NOT NULL
                )
                """
            )

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        # One connection per call: Streamlit runs scripts on worker threads.
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            with conn:  # commits on success, rolls back on error
                yield conn
        finally:
            conn.close()

    def list_projects(self) -> list[Project]:
        with self._conn() as conn:
            rows = conn.execute("SELECT payload FROM projects ORDER BY updated_at DESC").fetchall()
        return [Project.model_validate_json(row["payload"]) for row in rows]

    def get(self, project_id: int) -> Project | None:
        with self._conn() as conn:
            row = conn.execute("SELECT payload FROM projects WHERE id = ?", (project_id,)).fetchone()
        return Project.model_validate_json(row["payload"]) if row else None

    def save(self, project: Project) -> Project:
        """Insert or update a project and return it with its id set."""
        project.updated_at = utcnow()
        stamp = project.updated_at.isoformat()
        with self._conn() as conn:
            if project.id is None:
                cursor = conn.execute(
                    "INSERT INTO projects (title, stage, updated_at, payload) VALUES (?, ?, ?, '')",
                    (project.title, project.stage.value, stamp),
                )
                project.id = cursor.lastrowid
            conn.execute(
                "UPDATE projects SET title = ?, stage = ?, updated_at = ?, payload = ? WHERE id = ?",
                (project.title, project.stage.value, stamp, project.model_dump_json(), project.id),
            )
        return project

    def delete(self, project_id: int) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
