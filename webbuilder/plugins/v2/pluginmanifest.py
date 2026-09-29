"""webbuilder.plugins.v2.pluginmanifest — Plugin manifest data."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PluginManifest:
    """Metadata describing a plugin."""

    id: str = ""
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    entry_point: str = ""
    dependencies: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize manifest to a dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "entry_point": self.entry_point,
            "dependencies": self.dependencies,
            "permissions": self.permissions,
            "category": self.category,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginManifest":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            entry_point=data.get("entry_point", ""),
            dependencies=data.get("dependencies", []),
            permissions=data.get("permissions", []),
            category=data.get("category", "general"),
            metadata=data.get("metadata", {}),
        )
