from __future__ import annotations
from typing import Any, Dict, List


class ProjectSearch:
    def __init__(self, project_manager=None):
        self._projects = {}
        self._project_manager = project_manager

    def add_project(self, project):
        self._projects[project.id] = project

    def remove_project(self, project_id):
        self._projects.pop(project_id, None)

    def search(self, query, limit=None):
        query = query.lower()
        if not query:
            return []
        results = []
        for p in self._projects.values():
            if len(results) >= (limit or float('inf')):
                break
            if query in p.name.lower() or query in p.id.lower():
                results.append(p)
                continue
            for page in getattr(p, "pages", []):
                if query in page.name.lower():
                    results.append(p)
                    break
                for section in getattr(page, "sections", []):
                    props = getattr(section, "props", {})
                    for v in props.values():
                        if isinstance(v, str) and query in v.lower():
                            results.append(p)
                            break
                    else:
                        continue
                    break
                else:
                    continue
                break
        if limit is not None:
            return results[:limit]
        return results

    def index(self, project: Any):
        pass

    def reindex(self):
        pass
