"""webbuilder.plugins.pluginmanager — Plugin manager."""

from __future__ import annotations
import importlib
import inspect
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from webbuilder.plugins.v2.pluginmanifest import PluginManifest

logger = logging.getLogger("webbuilder.plugins")


class PluginManager:
    """Discovers, loads, and manages plugins."""

    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        self.plugins: Dict[str, Any] = {}
        self.plugin_dirs: List[str] = plugin_dirs or []
        self._loaded = False

    def discover(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Discover plugins in a directory or the configured search paths."""
        raise NotImplementedError("Use plugins.v2.PluginManager for full discovery")

    def load(self, module_name: str) -> Any:
        """Load a plugin by module name."""
        if module_name in self.plugins:
            return self.plugins[module_name]
        try:
            mod = importlib.import_module(module_name)
            self.plugins[module_name] = mod
            logger.info("Loaded plugin: %s", module_name)
            return mod
        except ImportError as e:
            logger.error("Failed to load plugin %s: %s", module_name, e)
            raise

    def get(self, name: str) -> Optional[Any]:
        """Retrieve a loaded plugin by name."""
        return self.plugins.get(name)

    def list(self) -> List[str]:
        """List loaded plugin names."""
        return list(self.plugins.keys())

    def register(self, name: str, plugin: Any) -> None:
        """Register a plugin instance or module."""
        self.plugins[name] = plugin
        logger.info("Registered plugin: %s", name)

    def unregister(self, name: str) -> None:
        """Remove a registered plugin."""
        self.plugins.pop(name, None)

    def discover_plugins(self) -> List[str]:
        return self.list()

    def get_all_plugins(self) -> List[Any]:
        return list(self.plugins.values())

    def get_plugin(self, name: str) -> Optional[Any]:
        return self.get(name)
