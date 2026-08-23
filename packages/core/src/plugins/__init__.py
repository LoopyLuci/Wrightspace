# WebBuilder Plugin Architecture
# Stable API for 100-year survival
# Version: 1.0.0

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pathlib import Path
import json
import importlib
import importlib.util
import sys
import os


class PluginInterface(ABC):
    """Base interface all plugins must implement"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version (semver)"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description"""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict) -> bool:
        """Initialize plugin with configuration"""
        pass
    
    @abstractmethod
    def shutdown(self):
        """Clean up plugin resources"""
        pass


class ComponentPlugin(PluginInterface):
    """Plugin for custom section components"""
    
    @abstractmethod
    def render(self, props: Dict) -> str:
        """Render component to HTML"""
        pass
    
    @abstractmethod
    def get_default_props(self) -> Dict:
        """Get default properties for this component"""
        pass
    
    @abstractmethod
    def get_prop_schema(self) -> Dict:
        """Get property schema for editor"""
        pass


class ExporterPlugin(PluginInterface):
    """Plugin for custom export formats"""
    
    @abstractmethod
    def export(self, project: Dict, output_path: str) -> str:
        """Export project to file"""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get file extension for this format"""
        pass


class ProviderPlugin(PluginInterface):
    """Plugin for AI providers"""
    
    @abstractmethod
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """Send chat messages and get response"""
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models"""
        pass
    
    @abstractmethod
    def validate_key(self, api_key: str) -> bool:
        """Validate API key"""
        pass


class ThemePlugin(PluginInterface):
    """Plugin for design themes"""
    
    @abstractmethod
    def get_css_variables(self) -> Dict:
        """Get CSS custom properties"""
        pass
    
    @abstractmethod
    def get_components(self) -> Dict:
        """Get component style overrides"""
        pass


class PluginRegistry:
    """Central registry for all plugins"""
    
    def __init__(self):
        self._plugins: Dict[str, PluginInterface] = {}
        self._components: Dict[str, ComponentPlugin] = {}
        self._exporters: Dict[str, ExporterPlugin] = {}
        self._providers: Dict[str, ProviderPlugin] = {}
        self._themes: Dict[str, ThemePlugin] = {}
    
    def register(self, plugin: PluginInterface):
        """Register a plugin"""
        self._plugins[plugin.name] = plugin
        
        if isinstance(plugin, ComponentPlugin):
            self._components[plugin.name] = plugin
        elif isinstance(plugin, ExporterPlugin):
            self._exporters[plugin.name] = plugin
        elif isinstance(plugin, ProviderPlugin):
            self._providers[plugin.name] = plugin
        elif isinstance(plugin, ThemePlugin):
            self._themes[plugin.name] = plugin
    
    def unregister(self, name: str):
        """Unregister a plugin"""
        if name in self._plugins:
            self._plugins[name].shutdown()
            del self._plugins[name]
        
        for registry in [self._components, self._exporters, self._providers, self._themes]:
            if name in registry:
                del registry[name]
    
    def get_component(self, name: str) -> Optional[ComponentPlugin]:
        return self._components.get(name)
    
    def get_exporter(self, name: str) -> Optional[ExporterPlugin]:
        return self._exporters.get(name)
    
    def get_provider(self, name: str) -> Optional[ProviderPlugin]:
        return self._providers.get(name)
    
    def get_theme(self, name: str) -> Optional[ThemePlugin]:
        return self._themes.get(name)
    
    def list_plugins(self) -> Dict:
        """List all registered plugins"""
        return {
            'components': list(self._components.keys()),
            'exporters': list(self._exporters.keys()),
            'providers': list(self._providers.keys()),
            'themes': list(self._themes.keys()),
        }


class PluginLoader:
    """Load plugins from filesystem"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.registry = PluginRegistry()
    
    def load_all(self):
        """Load all plugins from plugin directory"""
        if not self.plugin_dir.exists():
            return
        
        for plugin_path in self.plugin_dir.iterdir():
            if plugin_path.is_dir():
                self._load_plugin(plugin_path)
    
    def _load_plugin(self, plugin_path: Path):
        """Load a single plugin from directory"""
        manifest_path = plugin_path / "plugin.json"
        if not manifest_path.exists():
            return
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            entry_point = manifest.get('entry_point', 'main.py')
            module_path = plugin_path / entry_point
            
            if not module_path.exists():
                return
            
            # Load module
            spec = importlib.util.spec_from_file_location(
                f"plugin_{manifest['name']}", str(module_path)
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class
            plugin_class = getattr(module, manifest.get('class', 'Plugin'))
            plugin_instance = plugin_class()
            
            # Initialize and register
            config = manifest.get('config', {})
            if plugin_instance.initialize(config):
                self.registry.register(plugin_instance)
                
        except Exception as e:
            print(f"Failed to load plugin {plugin_path.name}: {e}")


# ============================================================================
# EXAMPLE PLUGINS
# ============================================================================

class HeroComponentPlugin(ComponentPlugin):
    """Example hero component plugin"""
    
    @property
    def name(self) -> str:
        return "custom-hero"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Custom hero section with animation"
    
    def initialize(self, config: Dict) -> bool:
        return True
    
    def shutdown(self):
        pass
    
    def render(self, props: Dict) -> str:
        return f'''
<section class="hero-custom" style="padding: 100px 20px; text-align: center; background: {props.get('bg', '#3b82f6')};">
  <h1 style="font-size: 48px; color: white;">{props.get('title', 'Welcome')}</h1>
  <p style="color: rgba(255,255,255,0.9);">{props.get('subtitle', 'Build something')}</p>
</section>
'''
    
    def get_default_props(self) -> Dict:
        return {'title': 'Welcome', 'subtitle': 'Build something', 'bg': '#3b82f6'}
    
    def get_prop_schema(self) -> Dict:
        return {
            'title': {'type': 'string', 'label': 'Title'},
            'subtitle': {'type': 'string', 'label': 'Subtitle'},
            'bg': {'type': 'color', 'label': 'Background'}
        }


class VueExporterPlugin(ExporterPlugin):
    """Example Vue.js exporter plugin"""
    
    @property
    def name(self) -> str:
        return "vue-exporter"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Export to Vue.js components"
    
    def initialize(self, config: Dict) -> bool:
        return True
    
    def shutdown(self):
        pass
    
    def export(self, project: Dict, output_path: str) -> str:
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        sections = project['pages'][0]['sections']
        
        for i, section in enumerate(sections):
            component = f'''<template>
  <section class="section">
    <h2>{section.get('props', {}).get('title', 'Section')}</h2>
    <p>{section.get('props', {}).get('subtitle', 'Description')}</p>
  </section>
</template>

<script setup>
// Component logic
</script>
'''
            with open(os.path.join(output_path, f'Section{i:02d}.vue'), 'w') as f:
                f.write(component)
        
        return output_path
    
    def get_file_extension(self) -> str:
        return ".vue"


# ============================================================================
# PLUGIN API VERSIONING
# ============================================================================

class PluginAPI:
    """Stable plugin API version"""
    
    VERSION = "1.0.0"
    MINIMUM_VERSION = "1.0.0"
    
    @staticmethod
    def check_compatibility(plugin_version: str) -> bool:
        """Check if plugin is compatible with current API"""
        # Simple semver check
        major, minor, patch = map(int, plugin_version.split('.'))
        min_major, min_minor, min_patch = map(int, PluginAPI.MINIMUM_VERSION.split('.'))
        
        if major != min_major:
            return False
        if minor < min_minor:
            return False
        return True


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    'PluginInterface', 'ComponentPlugin', 'ExporterPlugin', 'ProviderPlugin', 'ThemePlugin',
    'PluginRegistry', 'PluginLoader', 'PluginAPI',
    'HeroComponentPlugin', 'VueExporterPlugin'
]
