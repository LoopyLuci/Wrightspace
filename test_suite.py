# WebBuilder Test Suite
# Comprehensive tests for 100-year survival
# Run with: python -m pytest test_suite.py -v

import unittest
import json
import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from packages.core.src.export import ExportManager, HTMLExporter, ReactExporter, JSONExporter, ProjectSchema
from packages.core.src.plugins import PluginRegistry, HeroComponentPlugin, VueExporterPlugin


class TestProjectSchema(unittest.TestCase):
    """Test project schema validation and migration"""
    
    def test_validate_valid_project(self):
        project = {
            'id': 'test-123',
            'name': 'Test Project',
            'pages': [{'sections': []}],
            'design': {'colors': {}, 'fonts': {}}
        }
        self.assertTrue(ProjectSchema.validate(project))
    
    def test_validate_invalid_project(self):
        project = {'name': 'Test'}
        self.assertFalse(ProjectSchema.validate(project))
    
    def test_migrate_v1_to_v2(self):
        old_project = {
            'id': 'test',
            'name': 'Test',
            'pages': [],
            'colors': {'primary': '#3b82f6'},
            'fonts': {'heading': 'Inter'}
        }
        migrated = ProjectSchema.migrate(old_project)
        self.assertEqual(migrated['version'], '2.0.0')
        self.assertIn('design', migrated)
        self.assertNotIn('colors', migrated)


class TestHTMLExporter(unittest.TestCase):
    """Test HTML export functionality"""
    
    def setUp(self):
        self.project = {
            'id': 'test',
            'name': 'Test Project',
            'pages': [{
                'sections': [
                    {
                        'id': 'sec-1',
                        'type': 'hero-centered',
                        'props': {
                            'title': 'Welcome',
                            'subtitle': 'Test subtitle',
                            'ctaText': 'Get Started',
                            'backgroundColor': '#3b82f6'
                        }
                    },
                    {
                        'id': 'sec-2',
                        'type': 'footer',
                        'props': {
                            'copyright': '© 2024 Test',
                            'links': ['Privacy', 'Terms']
                        }
                    }
                ]
            }],
            'design': {
                'colors': {'primary': '#3b82f6', 'secondary': '#8b5cf6', 'bg': '#ffffff', 'text': '#1e293b'},
                'fonts': {'heading': 'Inter', 'body': 'Inter'}
            }
        }
        self.exporter = HTMLExporter(self.project)
    
    def test_generate_html(self):
        html = self.exporter.generate_html()
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('Test Project', html)
        self.assertIn('Welcome', html)
        self.assertIn('© 2024 Test', html)
    
    def test_export_creates_file(self):
        output_path = '/tmp/test_export.html'
        self.exporter.export(output_path)
        self.assertTrue(Path(output_path).exists())
        
        with open(output_path, 'r') as f:
            content = f.read()
        self.assertIn('<!DOCTYPE html>', content)
        
        os.remove(output_path)
    
    def test_render_hero_section(self):
        section = {'type': 'hero-centered', 'props': {'title': 'Test', 'subtitle': 'Sub', 'ctaText': 'CTA'}}
        html = self.exporter.render_section(section)
        self.assertIn('Test', html)
        self.assertIn('Sub', html)
        self.assertIn('CTA', html)
    
    def test_render_features_section(self):
        section = {
            'type': 'features-grid-3',
            'props': {
                'title': 'Features',
                'subtitle': 'Our features',
                'items': [{'title': 'Fast', 'description': 'Very fast', 'icon': '⚡'}]
            }
        }
        html = self.exporter.render_section(section)
        self.assertIn('Features', html)
        self.assertIn('Fast', html)
    
    def test_render_pricing_section(self):
        section = {
            'type': 'pricing-3-tiers',
            'props': {
                'title': 'Pricing',
                'tiers': [
                    {'name': 'Free', 'price': '$0', 'features': ['Basic']},
                    {'name': 'Pro', 'price': '$29', 'features': ['Pro']},
                    {'name': 'Enterprise', 'price': '$99', 'features': ['All']}
                ]
            }
        }
        html = self.exporter.render_section(section)
        self.assertIn('Free', html)
        self.assertIn('$0', html)
        self.assertIn('$29', html)
        self.assertIn('$99', html)


class TestReactExporter(unittest.TestCase):
    """Test React export functionality"""
    
    def setUp(self):
        self.project = {
            'id': 'test',
            'name': 'Test Project',
            'pages': [{
                'sections': [
                    {'id': 'sec-1', 'type': 'hero-centered', 'props': {'title': 'Welcome'}},
                    {'id': 'sec-2', 'type': 'footer', 'props': {'copyright': '© 2024'}}
                ]
            }],
            'design': {'colors': {'primary': '#3b82f6'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}}
        }
        self.exporter = ReactExporter(self.project)
    
    def test_export_creates_files(self):
        output_dir = '/tmp/test_react_export'
        self.exporter.export(output_dir)
        
        self.assertTrue(Path(output_dir).exists())
        self.assertTrue(Path(output_dir, 'package.json').exists())
        self.assertTrue(Path(output_dir, 'src', 'App.jsx').exists())
        self.assertTrue(Path(output_dir, 'src', 'index.jsx').exists())
        self.assertTrue(Path(output_dir, 'src', 'styles.css').exists())
        
        # Clean up
        import shutil
        shutil.rmtree(output_dir)
    
    def test_package_json_content(self):
        output_dir = '/tmp/test_react_export'
        self.exporter.export(output_dir)
        
        with open(Path(output_dir, 'package.json'), 'r') as f:
            package = json.load(f)
        
        self.assertIn('react', package['dependencies'])
        self.assertIn('scripts', package)
        
        import shutil
        shutil.rmtree(output_dir)


class TestJSONExporter(unittest.TestCase):
    """Test JSON export functionality"""
    
    def setUp(self):
        self.project = {
            'id': 'test',
            'name': 'Test Project',
            'pages': [{'sections': []}],
            'design': {'colors': {}, 'fonts': {}}
        }
        self.exporter = JSONExporter(self.project)
    
    def test_export_creates_valid_json(self):
        output_path = '/tmp/test_export.json'
        self.exporter.export(output_path)
        
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn('version', data)
        self.assertIn('exported_at', data)
        self.assertIn('project', data)
        self.assertEqual(data['project']['name'], 'Test Project')
        
        os.remove(output_path)


class TestExportManager(unittest.TestCase):
    """Test export manager"""
    
    def setUp(self):
        self.project = {
            'id': 'test',
            'name': 'Test Project',
            'pages': [{'sections': []}],
            'design': {'colors': {}, 'fonts': {}}
        }
        self.manager = ExportManager(self.project)
    
    def test_export_all(self):
        output_dir = '/tmp/test_export_all'
        results = self.manager.export_all(output_dir)
        
        self.assertIn('html', results)
        self.assertIn('react', results)
        self.assertIn('json', results)
        
        self.assertTrue(Path(results['html']).exists())
        self.assertTrue(Path(results['react']).exists())
        self.assertTrue(Path(results['json']).exists())
        
        # Clean up
        import shutil
        shutil.rmtree(output_dir)
    
    def test_invalid_format_raises(self):
        with self.assertRaises(ValueError):
            self.manager.export('invalid', '/tmp/test')


class TestPluginRegistry(unittest.TestCase):
    """Test plugin registry"""
    
    def setUp(self):
        self.registry = PluginRegistry()
    
    def test_register_component_plugin(self):
        plugin = HeroComponentPlugin()
        self.registry.register(plugin)
        
        self.assertIn('custom-hero', self.registry.list_plugins()['components'])
    
    def test_register_exporter_plugin(self):
        plugin = VueExporterPlugin()
        self.registry.register(plugin)
        
        self.assertIn('vue-exporter', self.registry.list_plugins()['exporters'])
    
    def test_get_plugin(self):
        plugin = HeroComponentPlugin()
        self.registry.register(plugin)
        
        retrieved = self.registry.get_component('custom-hero')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, 'custom-hero')
    
    def test_unregister_plugin(self):
        plugin = HeroComponentPlugin()
        self.registry.register(plugin)
        self.registry.unregister('custom-hero')
        
        self.assertNotIn('custom-hero', self.registry.list_plugins()['components'])


class TestComponentPlugin(unittest.TestCase):
    """Test component plugin functionality"""
    
    def test_hero_plugin_render(self):
        plugin = HeroComponentPlugin()
        props = plugin.get_default_props()
        html = plugin.render(props)
        
        self.assertIn('hero-custom', html)
        self.assertIn('Welcome', html)
    
    def test_hero_plugin_schema(self):
        plugin = HeroComponentPlugin()
        schema = plugin.get_prop_schema()
        
        self.assertIn('title', schema)
        self.assertIn('subtitle', schema)
        self.assertIn('bg', schema)


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility"""
    
    def test_old_project_format_loads(self):
        old_project = {
            'id': 'old-project',
            'name': 'Old Project',
            'pages': [{'sections': []}],
            'colors': {'primary': '#ff0000'},
            'fonts': {'heading': 'Arial'}
        }
        
        migrated = ProjectSchema.migrate(old_project)
        self.assertTrue(ProjectSchema.validate(migrated))
    
    def test_v2_project_passes_validation(self):
        project = {
            'id': 'v2-project',
            'name': 'V2 Project',
            'pages': [{'sections': []}],
            'design': {
                'colors': {'primary': '#3b82f6'},
                'fonts': {'heading': 'Inter', 'body': 'Inter'}
            },
            'version': '2.0.0'
        }
        
        self.assertTrue(ProjectSchema.validate(project))


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_export_pipeline(self):
        """Test complete export pipeline"""
        project = {
            'id': 'integration-test',
            'name': 'Integration Test',
            'pages': [{
                'sections': [
                    {'id': 's1', 'type': 'hero-centered', 'props': {'title': 'Welcome', 'subtitle': 'Test', 'ctaText': 'Go'}},
                    {'id': 's2', 'type': 'features-grid-3', 'props': {'title': 'Features', 'items': [{'title': 'Fast', 'description': 'Quick', 'icon': '⚡'}]}},
                    {'id': 's3', 'type': 'footer', 'props': {'copyright': '© 2024', 'links': ['Privacy']}}
                ]
            }],
            'design': {
                'colors': {'primary': '#3b82f6', 'secondary': '#8b5cf6', 'bg': '#ffffff', 'text': '#1e293b'},
                'fonts': {'heading': 'Inter', 'body': 'Inter'}
            }
        }
        
        # Export to HTML
        html_exporter = HTMLExporter(project)
        html = html_exporter.generate_html()
        
        self.assertIn('Welcome', html)
        self.assertIn('Features', html)
        self.assertIn('Fast', html)
        self.assertIn('© 2024', html)
        
        # Verify HTML is valid (basic check)
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('</html>', html)
    
    def test_plugin_rendering_pipeline(self):
        """Test plugin rendering in project"""
        registry = PluginRegistry()
        hero_plugin = HeroComponentPlugin()
        registry.register(hero_plugin)
        
        component = registry.get_component('custom-hero')
        self.assertIsNotNone(component)
        
        html = component.render(component.get_default_props())
        self.assertIn('hero-custom', html)


if __name__ == '__main__':
    unittest.main()
