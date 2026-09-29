"""webbuilder.plugins.v2.pluginapi — Plugin API exposed to plugins."""

from __future__ import annotations
import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger("webbuilder.plugins")


class PluginAPI:
    """API exposed to plugins for interacting with WebBuilder.

    Plugins receive a PluginAPI instance that lets them register commands,
    access project data, and interact with the GUI.
    """

    def __init__(self, plugin_manager=None, config=None):
        self.plugin_manager = plugin_manager
        self.config = config
        self._app = plugin_manager
        self._commands: Dict[str, Callable] = {}
        self._hooks: Dict[str, List[Callable]] = {}

    @property
    def app(self) -> Any:
        """The running application instance (if any)."""
        return self._app

    def register_command(self, name: str, handler: Callable) -> None:
        """Register a command handler."""
        self._commands[name] = handler

    def get_command(self, name: str) -> Callable:
        """Retrieve a registered command handler."""
        return self._commands[name]

    def list_commands(self) -> List[str]:
        """List all registered command names."""
        return list(self._commands.keys())

    def register_hook(self, hook_name: str, handler: Callable) -> None:
        """Register a hook handler."""
        self._hooks.setdefault(hook_name, []).append(handler)

    def run_hooks(self, hook_name: str, *args: Any, **kwargs: Any) -> List[Any]:
        """Run all handlers registered for a hook."""
        results: List[Any] = []
        for handler in self._hooks.get(hook_name, []):
            try:
                results.append(handler(*args, **kwargs))
            except Exception as e:
                logger.warning("Hook '%s' handler %s failed: %s", hook_name, getattr(handler, '__name__', '?'), e)
        return results

    def get_project(self) -> Any:
        """Return the current project."""
        if self._app and hasattr(self._app, "project"):
            return self._app.project
        return None
