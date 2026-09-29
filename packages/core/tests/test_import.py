import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from export import HTMLExporter

project = {
    'id': 'test',
    'name': 'Test Project',
    'pages': [{
        'sections': [
            {'id': 's1', 'type': 'hero-centered', 'props': {'title': 'Welcome', 'subtitle': 'Test', 'ctaText': 'Go', 'backgroundColor': '#3b82f6'}},
            {'id': 's2', 'type': 'features-grid-3', 'props': {'title': 'Features', 'items': [{'title': 'Fast', 'description': 'Quick', 'icon': '⚡'}]}},
            {'id': 's3', 'type': 'footer', 'props': {'copyright': '© 2024', 'links': ['Privacy']}}
        ]
    }],
    'design': {'colors': {'primary': '#3b82f6', 'secondary': '#8b5cf6', 'bg': '#ffffff', 'text': '#1e293b'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}}
}

exporter = HTMLExporter(project)
html = exporter.generate()
print('HTML generated successfully!')
print(f'Length: {len(html)} chars')
print('Contains Welcome:', 'Welcome' in html)
print('Contains Features:', 'Features' in html)
print('Contains Footer:', '© 2024' in html)
