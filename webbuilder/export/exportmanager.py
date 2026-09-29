"""webbuilder.export.exportmanager — Manages multiple export backends."""

from __future__ import annotations
from typing import Dict, Type, Any, Optional, List

from webbuilder.export.htmlexporter import HTMLExporter
from webbuilder.export.jsonexporter import JSONExporter
from webbuilder.export.reactexporter import ReactExporter
from webbuilder.export.vueexporter import VueExporter


class ExportManager:
    """Coordinates export to multiple formats (HTML, JSON, React, Vue)."""

    def __init__(self):
        self.backends: Dict[str, Any] = {}
        self._register_default_backends()

    def _register_default_backends(self) -> None:
        """Register the default export backends."""
        self.backends["html"] = HTMLExporter
        self.backends["json"] = JSONExporter
        self.backends["react"] = ReactExporter
        self.backends["vue"] = VueExporter

    def register(self, name: str, backend_cls: Type[Any]) -> None:
        """Register a custom export backend.

        Args:
            name: Format identifier (e.g., 'pdf').
            backend_cls: Class to instantiate for this format.
        """
        self.backends[name] = backend_cls

    def get_backend(self, name: str) -> Optional[Type[Any]]:
        """Retrieve a backend class by name.

        Args:
            name: Format identifier.

        Returns:
            The backend class, or None if not registered.
        """
        return self.backends.get(name)

    def list_backends(self) -> List[str]:
        return sorted(self.backends.keys())

    def get_supported_formats(self) -> List[str]:
        return sorted(self.backends.keys())

    def export(self, project: "Project", fmt: str, output_path: Any) -> Any:
        """Export a project to the specified format.

        Args:
            project: The Project to export.
            fmt: Format identifier.
            output_path: Destination path.

        Raises:
            ValueError: If the format is not supported.
        """
        backend_cls = self.backends.get(fmt)
        if backend_cls is None:
            raise ValueError(f"Unsupported export format: {fmt}")
        backend = backend_cls()
        return backend.export(project, output_path)
