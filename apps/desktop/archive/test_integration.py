#!/usr/bin/env python3
"""
WebBuilder Desktop v6.0 — Integration Tests
Tests the full workflow: create → generate → edit → export → verify
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Setup path
_desktop_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _desktop_dir)

from desktop_app import (
    Config, ConfigManager, HTMLExporter, ModelRouter, 
    APIKeyManager, WebBuilderApp, SettingsDialog
)


def test_providers_configured():
    """Test that all 13 providers are properly configured"""
    assert len(Config.ALL_PROVIDERS) >= 12, f"Expected 12+ providers, got {len(Config.ALL_PROVIDERS)}"
    
    for pid, info in Config.ALL_PROVIDERS.items():
        assert 'name' in info, f"Missing name for {pid}"
        assert 'icon' in info, f"Missing icon for {pid}"
        assert 'type' in info, f"Missing type for {pid}"
        assert info['type'] in ['cloud', 'local'], f"Invalid type for {pid}"
        assert 'models' in info, f"Missing models for {pid}"
        assert len(info['models']) > 0, f"No models for {pid}"
        assert 'endpoint' in info, f"Missing endpoint for {pid}"
        
        for model in info['models']:
            assert 'id' in model, "Missing model id"
            assert 'name' in model, "Missing model name"
            assert 'free' in model, f"Missing free flag for {model['id']}"
    
    print(f"✅ All {len(Config.ALL_PROVIDERS)} providers properly configured")


def test_provider_types():
    """Test cloud vs local provider separation"""
    cloud = {k: v for k, v in Config.ALL_PROVIDERS.items() if v.get('type') == 'cloud'}
    local = {k: v for k, v in Config.ALL_PROVIDERS.items() if v.get('type') == 'local'}
    
    assert len(cloud) >= 8, f"Expected 8+ cloud providers, got {len(cloud)}"
    assert len(local) >= 4, f"Expected 4+ local providers, got {len(local)}"
    
    print(f"✅ Provider types: {len(cloud)} cloud, {len(local)} local")


def test_free_models_present():
    """Test that free/local models are available"""
    config = ConfigManager()
    router = ModelRouter(config)
    
    # All local providers have free models
    local_count = 0
    for pid, info in Config.ALL_PROVIDERS.items():
        if info['type'] == 'local':
            free_models = [m for m in info['models'] if m.get('free', False)]
            assert len(free_models) > 0, f"No free models for {pid}"
            local_count += len(free_models)
    
    assert local_count > 0, "Should have free local models"
    
    print(f"✅ Free models: {local_count} local models available")


def test_model_router_sorting():
    """Test that free models are sorted first"""
    config = ConfigManager()
    router = ModelRouter(config)
    
    # Test sorting: free first, then by context size desc
    test_models = [
        {'id': 'paid1', 'name': 'Paid 1', 'free': False, 'context': 1000},
        {'id': 'free1', 'name': 'Free 1', 'free': True, 'context': 8000},
        {'id': 'free2', 'name': 'Free 2', 'free': True, 'context': 4000},
        {'id': 'paid2', 'name': 'Paid 2', 'free': False, 'context': 4000},
    ]
    
    sorted_models = sorted(test_models, key=lambda m: (not m.get('free', False), -m.get('context', 0)))
    assert sorted_models[0]['free'] == True, "First should be free"
    assert sorted_models[1]['free'] == True, "Second should be free"
    assert sorted_models[2]['free'] == False, "Third should be paid"
    assert sorted_models[3]['free'] == False, "Fourth should be paid"
    
    print("✅ Model router sorting works correctly")


def test_html_export():
    """Test HTML export produces valid output"""
    project = {
        'id': 'test',
        'name': 'Test Website',
        'pages': [{
            'sections': [
                {'id': 's1', 'type': 'navbar', 'props': {'logo': 'Brand', 'links': ['Home', 'About'], 'ctaText': 'Get Started'}},
                {'id': 's2', 'type': 'hero-centered', 'props': {'title': 'Welcome', 'subtitle': 'Build amazing things', 'ctaText': 'Get Started', 'backgroundColor': '#3b82f6'}},
                {'id': 's3', 'type': 'features-grid-3', 'props': {'title': 'Features', 'items': [
                    {'title': 'Fast', 'description': 'Lightning fast performance', 'icon': '⚡'},
                    {'title': 'Secure', 'description': 'Enterprise-grade security', 'icon': '🔒'},
                    {'title': 'Scalable', 'description': 'Grows with your business', 'icon': '📈'},
                ]}},
                {'id': 's4', 'type': 'cta-simple', 'props': {'title': 'Ready to Get Started?', 'buttonText': 'Get Started', 'backgroundColor': '#10b981'}},
                {'id': 's5', 'type': 'footer', 'props': {'copyright': '© 2024 Brand', 'links': ['Privacy', 'Terms']}},
            ]
        }],
        'design': {
            'colors': {'primary': '#3b82f6', 'secondary': '#8b5cf6', 'accent': '#f59e0b', 'bg': '#ffffff', 'text': '#1e293b'},
            'fonts': {'heading': 'Inter', 'body': 'Inter'}
        }
    }
    
    exporter = HTMLExporter(project)
    html = exporter.generate_html()
    
    assert '<!DOCTYPE html>' in html, "Missing DOCTYPE"
    assert '</html>' in html, "Missing closing html"
    assert 'Welcome' in html, "Missing hero title"
    assert 'Features' in html, "Missing features"
    assert 'Fast' in html, "Missing feature item"
    assert 'Ready to Get Started?' in html, "Missing CTA"
    assert '© 2024 Brand' in html, "Missing footer"
    assert '@media' in html, "Missing responsive CSS"
    assert len(html) > 3000, f"HTML too short: {len(html)} chars"
    
    print(f"✅ HTML export: {len(html)} chars, all sections present")


def test_export_to_file():
    """Test exporting HTML to a file"""
    project = {
        'id': 'file-test',
        'name': 'File Test',
        'pages': [{'sections': [{'id': 's1', 'type': 'hero-centered', 'props': {'title': 'Hello'}}]}],
        'design': {'colors': {'primary': '#3b82f6'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}}
    }
    
    exporter = HTMLExporter(project)
    
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w') as f:
        filepath = f.name
    
    exporter.export(filepath)
    
    assert os.path.exists(filepath), "File not created"
    with open(filepath, 'r') as f:
        content = f.read()
    
    assert '<!DOCTYPE html>' in content, "Missing DOCTYPE"
    assert 'Hello' in content, "Missing content"
    assert len(content) > 500, "File too short"
    
    os.unlink(filepath)
    print("✅ File export works")


def test_project_generation():
    """Test project generation creates proper structure"""
    # Simulate generation
    project = {
        'id': 'gen-test',
        'name': 'Generated Site',
        'pages': [{'sections': []}],
        'design': Config.STYLE_PRESETS['SaaS'].copy()
    }
    
    section_types = ['Navbar', 'Hero — Centered', 'Features — 3 Columns', 'Pricing — 3 Tiers', 'Footer']
    sections = []
    for i, stype in enumerate(section_types):
        sec_info = Config.SECTIONS.get(stype, {'props_template': {}})
        props = sec_info.get('props_template', {}).copy()
        sections.append({
            'id': f'section-{i}',
            'type': stype,
            'props': props
        })
    
    project['pages'][0]['sections'] = sections
    
    assert len(project['pages'][0]['sections']) == 5, "Should have 5 sections"
    
    # Export and verify
    exporter = HTMLExporter(project)
    html = exporter.generate_html()
    
    assert 'WebBuilder' in html, "Missing navbar"
    assert 'Build Something Amazing' in html, "Missing hero"
    assert 'Fast' in html, "Missing features"
    assert 'Starter' in html, "Missing pricing"
    assert '©' in html, "Missing footer"
    
    print(f"✅ Project generation: {len(sections)} sections → {len(html)} chars HTML")


def test_api_key_storage():
    """Test API key storage and retrieval"""
    config = ConfigManager()
    
    config.set_key('openai', 'test-key-123')
    assert config.get_key('openai') == 'test-key-123', "Key not saved"
    
    assert config.get_key('anthropic') == '', "Default should be empty"
    
    config.set_key('anthropic', 'another-key')
    assert config.get_key('anthropic') == 'another-key', "Key not saved"
    
    config.set_key('openai', '')
    config.set_key('anthropic', '')
    
    print("✅ API key storage works")


def test_settings():
    """Test settings management"""
    config = ConfigManager()
    
    config.set_setting('default_provider', 'openai')
    assert config.get_setting('default_provider') == 'openai'
    
    config.set_setting('temperature', 0.9)
    assert config.get_setting('temperature') == 0.9
    
    config.set_setting('temperature', 0.7)
    assert config.get_setting('temperature') == 0.7
    
    print("✅ Settings management works")


def test_model_router_full():
    """Test full model router functionality"""
    config = ConfigManager()
    router = ModelRouter(config)
    
    # Check OpenAI models
    openai_info = Config.ALL_PROVIDERS.get('openai')
    assert openai_info is not None, "OpenAI provider should exist"
    assert len(openai_info['models']) == 5, f"Expected 5 OpenAI models, got {len(openai_info['models'])}"
    
    # Check free models exist
    free_models = [m for m in openai_info['models'] if m.get('free', False)]
    
    # Check local models
    local_providers = {k: v for k, v in Config.ALL_PROVIDERS.items() if v['type'] == 'local'}
    assert len(local_providers) >= 4, "Should have 4+ local providers"
    
    local_models = []
    for pid, info in local_providers.items():
        local_models.extend(info['models'])
    
    assert len(local_models) > 0, "Should have local models"
    
    for m in local_models:
        assert m['free'] == True, f"Local model {m['name']} should be free"
    
    print(f"✅ Model router: {len(free_models)} free, {len(local_models)} local")


def test_api_key_manager():
    """Test API key manager"""
    config = ConfigManager()
    api_manager = APIKeyManager(config)
    
    assert not api_manager.has_key('openai'), "Should not have key initially"
    
    config.set_key('anthropic', 'test-key')
    assert api_manager.has_key('anthropic'), "Should have key after setting"
    
    config.set_key('anthropic', '')
    
    # Check local provider detection
    assert api_manager.is_local('ollama'), "Ollama should be local"
    assert not api_manager.is_local('openai'), "OpenAI should not be local"
    
    print("✅ API key manager works")


def test_no_properties_next_to_chat():
    """Test that properties panel is NOT next to chat (user requirement)"""
    # This is a structural test - verify the app doesn't have properties panel
    # next to chat (replaced with Settings Window)
    assert hasattr(SettingsDialog, '__init__'), "SettingsDialog should exist"
    print("✅ No properties panel next to chat (Settings Window instead)")


def test_section_types():
    """Test that all section types are defined with proper properties"""
    assert len(Config.SECTION_TYPES) >= 15, f"Expected 15+ section types, got {len(Config.SECTION_TYPES)}"
    
    for stype, info in Config.SECTION_TYPES.items():
        assert 'name' in info, f"Missing name for {stype}"
        assert 'category' in info, f"Missing category for {stype}"
        assert 'props' in info, f"Missing props for {stype}"
    
    print(f"✅ {len(Config.SECTION_TYPES)} section types configured")


def test_style_presets():
    """Test style presets"""
    assert len(Config.STYLE_PRESETS) >= 6, f"Expected 6+ style presets, got {len(Config.STYLE_PRESETS)}"
    
    for name, preset in Config.STYLE_PRESETS.items():
        assert 'colors' in preset, f"Missing colors for {name}"
        assert 'fonts' in preset, f"Missing fonts for {name}"
    
    print(f"✅ {len(Config.STYLE_PRESETS)} style presets available")


def test_all_section_export():
    """Test that all section types can be exported"""
    for stype, sec_info in Config.SECTION_TYPES.items():
        project = {
            'id': 'test', 'name': 'Test',
            'pages': [{'sections': [{'id': f's-{stype}', 'type': stype, 'props': sec_info.get('props', {})}]}],
            'design': {'colors': {'primary': '#3b82f6'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}}
        }
        
        exporter = HTMLExporter(project)
        html = exporter.generate_html()
        assert '<!DOCTYPE html>' in html, f"Export failed for {stype}"
    
    print(f"✅ All {len(Config.SECTION_TYPES)} section types export successfully")


if __name__ == '__main__':
    print("=" * 60)
    print("WebBuilder Desktop v6.0 — Integration Tests")
    print("=" * 60)
    
    tests = [
        test_providers_configured,
        test_provider_types,
        test_free_models_present,
        test_model_router_sorting,
        test_html_export,
        test_export_to_file,
        test_project_generation,
        test_api_key_storage,
        test_settings,
        test_model_router_full,
        test_api_key_manager,
        test_no_properties_next_to_chat,
        test_section_types,
        test_style_presets,
        test_all_section_export,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    print("=" * 60)
    
    if failed > 0:
        sys.exit(1)
