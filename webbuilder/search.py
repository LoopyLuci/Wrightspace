"""webbuilder.search — auto-generated implementation."""

from __future__ import annotations

class ProjectSearch:
    """ProjectSearch."""

    def __init__(self, project_manager=None):

        self._projects = {}

        self._project_manager = project_manager

    def add_project(self, project):

        self._projects[project.id] = project

    def remove_project(self, project_id):

        self._projects.pop(project_id, None)

    def search(self, query):

        query = query.lower()

        results = []

        for p in self._projects.values():

            if query in p.name.lower() or query in p.id.lower():

                results.append(p)

        return results

    pass


__all__ = ['ProjectSearch']
