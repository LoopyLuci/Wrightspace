"""webbuilder.plugins — auto-generated implementation."""

from __future__ import annotations

class PluginManager:
    """PluginManager."""

    def __init__(self):

        self._plugins = {}

    def discover_plugins(self):

        return []

    def get_all_plugins(self):

        return list(self._plugins.values())

    def get_plugin(self, name):

        return self._plugins.get(name)

    pass


__all__ = ['PluginManager']
