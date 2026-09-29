"""webbuilder.plugins.v2.pluginmanager — V2 plugin manager."""

from __future__ import annotations
import importlib
import importlib.util
import inspect
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from webbuilder.plugins.v2.pluginmanifest import PluginManifest
from webbuilder.plugins.v2.pluginapi import PluginAPI

logger = logging.getLogger("webbuilder.plugins.v2")


class PluginManager:
    """Discovers and manages plugins via manifests."""

    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        self._plugins: Dict[str, Dict[str, Any]] = {}
        self._api: Optional[PluginAPI] = None
        self._plugin_dirs: List[str] = plugin_dirs or [".webbuilder/plugins"]

    def discover(self, path: Optional[str] = None) -> List[PluginManifest]:
        """Discover plugins in the given directory or configured search paths."""
        search_dirs = [Path(path)] if path else [Path(d) for d in self._plugin_dirs]
        manifests: List[PluginManifest] = []

        for directory in search_dirs:
            if not directory.exists():
                continue
            for entry in sorted(directory.iterdir()):
                if not entry.is_dir():
                    continue
                manifest_file = entry / "manifest.json"
                if manifest_file.exists():
                    try:
                        import json
                        manifest = PluginManifest.from_dict(json.loads(manifest_file.read_text()))
                        manifests.append(manifest)
                        logger.info("Discovered plugin: %s v%s", manifest.name, manifest.version)
                    except Exception as e:
                        logger.error("Failed to load manifest %s: %s", manifest_file, e)
                else:
                    # Try loading from __init__.py with manifest attribute
                    init_file = entry / "__init__.py"
                    if init_file.exists():
                        try:
                            mod = importlib.import_module(f"webbuilder.plugins.discovered.{entry.name}")
                            if hasattr(mod, "manifest"):
                                if isinstance(mod.manifest, dict):
                                    m = PluginManifest.from_dict(mod.manifest)
                                else:
                                    m = mod.manifest
                                manifests.append(m)
                        except ImportError:
                            continue

        for manifest in manifests:
            self._plugins[manifest.name] = {"manifest": manifest}
        return manifests

    def load(self, name: str, api: Optional[PluginAPI] = None) -> Any:
        """Load a discovered plugin by name.

        Args:
            name: Plugin name from the manifest.
            api: PluginAPI to pass to the plugin.

        Returns:
            The loaded plugin instance or module.

        Raises:
            ValueError: If plugin not found.
        """
        if name not in self._plugins:
            raise ValueError(f"Plugin not found: {name}")
        info = self._plugins[name]
        if "instance" in info:
            return info["instance"]

        manifest: PluginManifest = info["manifest"]
        if not manifest.entry_point:
            raise ValueError(f"No entry point for plugin: {name}")

        if api is None:
            api = PluginAPI()

        try:
            mod = importlib.import_module(manifest.entry_point)
        except ImportError:
            # Try loading as a relative path
            for d in self._plugin_dirs:
                mod_path = Path(d) / name / "__init__.py"
                if mod_path.exists():
                    mod = importlib.import_module(f"webbuilder.plugins.discovered.{name}")
                    break
            else:
                raise

        # Check if it's a callable that returns an instance
        if callable(mod):
            instance = mod(api)
        elif hasattr(mod, "Plugin"):
            instance = mod.Plugin(api)
        elif hasattr(mod, "get_plugin"):
            instance = mod.get_plugin(api)
        else:
            instance = mod

        info["instance"] = instance
        self._api = api
        logger.info("Loaded plugin: %s", name)
        return instance

    def get_all(self) -> Dict[str, Any]:
        """Return all discovered plugins."""
        return {name: self._plugins[name]["manifest"].to_dict() for name in self._plugins}

    def get(self, name: str) -> Any:
        """Get a plugin by name."""
        if name not in self._plugins:
            raise ValueError(f"Plugin not found: {name}")
        return self._plugins[name].get("instance")

    def list(self) -> List[str]:
        """List all plugin names."""
        return list(self._plugins.keys())

    def is_loaded(self, name: str) -> bool:
        """Check if a plugin is loaded (has an instance)."""
        return name in self._plugins and "instance" in self._plugins[name]

    def set_api(self, api: PluginAPI) -> None:
        """Set the API for all future plugin loads."""
        self._api = api

    def get_all_plugins(self) -> list:
        return list(self._plugins.values())
