"""webbuilder.core.multi.multipageproject — Multi-page project."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from webbuilder.core import Project


@dataclass
class MultiPageProject(Project):
    """A project with multiple pages and shared resources."""
    pages: List[Any] = field(default_factory=list)
    shared_assets: List[str] = field(default_factory=list)
    routing: Dict[str, str] = field(default_factory=dict)
    default_page: str = ""

    def add_page(self, name: str) -> Any:
        from webbuilder.core import Page
        page_id = f"page-{len(self.pages) + 1}"
        page = Page(id=page_id, name=name)
        self.pages.append(page)
        return page

    def get_page(self, page_id: str) -> Optional[Any]:
        for page in self.pages:
            if getattr(page, "id", None) == page_id:
                return page
        return None

    def remove_page(self, page_id: str) -> bool:
        if len(self.pages) <= 1:
            return False
        for i, page in enumerate(self.pages):
            if getattr(page, "id", None) == page_id:
                self.pages.pop(i)
                return True
        return False

    def duplicate_page(self, page_id: str) -> Optional[Any]:
        page = self.get_page(page_id)
        if page is None:
            return None
        from webbuilder.core import Page
        new_id = f"page-{len(self.pages) + 1}"
        dup = Page(id=new_id, name=f"{page.name} Copy")
        self.pages.append(dup)
        return dup

    def reorder_pages(self, page_ids: List[str]) -> None:
        page_map = {getattr(p, "id", None): p for p in self.pages}
        reordered = []
        for pid in page_ids:
            if pid in page_map:
                reordered.append(page_map[pid])
        self.pages = reordered

    def to_dict(self) -> Dict[str, Any]:
        base = {"id": self.id, "name": self.name, "description": getattr(self, "description", ""),
                "created_at": self.created_at, "pages": []}
        for page in self.pages:
            if hasattr(page, "to_dict"):
                base["pages"].append(page.to_dict())
            elif hasattr(page, "__dict__"):
                base["pages"].append(page.__dict__)
        base["routing"] = self.routing
        base["default_page"] = self.default_page
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MultiPageProject":
        project = cls(
            id=data.get("id", ""), name=data.get("name", ""),
            description=data.get("description", ""),
        )
        project.created_at = data.get("created_at", "")
        for page_data in data.get("pages", []):
            from webbuilder.core import Page
            page = Page.from_dict(page_data) if isinstance(page_data, dict) else page_data
            project.pages.append(page)
        project.routing = data.get("routing", {})
        project.default_page = data.get("default_page", "")
        return project

    def export_routes(self) -> Dict[str, str]:
        routes = {"/": self.default_page}
        for page in self.pages:
            path = getattr(page, "url", getattr(page, "path", ""))
            if path:
                routes[path] = getattr(page, "id", str(len(routes)))
        return routes
