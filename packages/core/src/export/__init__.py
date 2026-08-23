# WebBuilder Export System
# Export projects to open standards that outlive this platform
# Static HTML/CSS/JS, React, Vue, JSON

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class ProjectSchema:
    """Versioned project schema for backward compatibility"""
    
    VERSION = "2.0.0"
    
    @staticmethod
    def validate(project: Dict) -> bool:
        """Validate project structure"""
        required = ['id', 'name', 'pages', 'design']
        return all(k in project for k in required)
    
    @staticmethod
    def migrate(project: Dict) -> Dict:
        """Migrate old project format to current version"""
        version = project.get('version', '1.0.0')
        
        if version == '1.0.0':
            # Migrate from v1 to v2
            project['design'] = {
                'colors': project.get('colors', {}),
                'fonts': project.get('fonts', {'heading': 'Inter', 'body': 'Inter'})
            }
            del project['colors']
            del project['fonts']
            project['version'] = '2.0.0'
        
        return project


class HTMLExporter:
    """Export project to static HTML/CSS/JS"""
    
    def __init__(self, project: Dict):
        self.project = project
        self.design = project.get('design', {})
        self.colors = self.design.get('colors', {})
        self.fonts = self.design.get('fonts', {'heading': 'Inter', 'body': 'Inter'})
    
    def export(self, output_path: str) -> str:
        """Export project to HTML file"""
        html = self.generate_html()
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
    
    def generate_html(self) -> str:
        """Generate complete HTML document"""
        sections = self.project['pages'][0]['sections']
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="generator" content="WebBuilder">
  <title>{self.project['name']}</title>
  <style>
    :root {{
      --color-primary: {self.colors.get('primary', '#3b82f6')};
      --color-secondary: {self.colors.get('secondary', '#8b5cf6')};
      --color-accent: {self.colors.get('accent', '#f59e0b')};
      --color-bg: {self.colors.get('bg', '#ffffff')};
      --color-text: {self.colors.get('text', '#1e293b')};
      --font-heading: '{self.fonts.get('heading', 'Inter')}', sans-serif;
      --font-body: '{self.fonts.get('body', 'Inter')}', sans-serif;
    }}
    
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    body {{
      font-family: var(--font-body);
      color: var(--color-text);
      background: var(--color-bg);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
      font-family: var(--font-heading);
      font-weight: 700;
      line-height: 1.2;
    }}
    
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 20px;
    }}
    
    .btn {{
      display: inline-block;
      padding: 12px 24px;
      background: var(--color-primary);
      color: white;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      text-decoration: none;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    
    .btn:hover {{
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }}
    
    .section {{
      padding: 80px 0;
    }}
    
    @media (max-width: 768px) {{
      .section {{ padding: 40px 0; }}
      .container {{ padding: 0 16px; }}
    }}
  </style>
</head>
<body>
  <main>
'''
        
        for section in sections:
            html += self.render_section(section)
        
        html += f'''
  </main>
  
  <script>
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(a => {{
      a.addEventListener('click', e => {{
        e.preventDefault();
        const target = document.querySelector(a.getAttribute('href'));
        if (target) target.scrollIntoView({{ behavior: 'smooth' }});
      }});
    }});
  </script>
</body>
</html>'''
        
        return html
    
    def render_section(self, section: Dict) -> str:
        """Render a single section to HTML"""
        section_type = section['type']
        props = section.get('props', {})
        
        renderers = {
            'hero-centered': self._render_hero_centered,
            'hero-split': self._render_hero_split,
            'features-grid-3': self._render_features_grid,
            'features-grid-4': self._render_features_grid,
            'features-cards': self._render_features_cards,
            'stats-3-col': self._render_stats,
            'stats-4-col': self._render_stats,
            'pricing-3-tiers': self._render_pricing,
            'pricing-2-tiers': self._render_pricing,
            'cta-simple': self._render_cta_simple,
            'cta-split': self._render_cta_split,
            'testimonials-2-col': self._render_testimonials,
            'testimonials-3-col': self._render_testimonials,
            'faq-accordion': self._render_faq,
            'footer': self._render_footer,
            'navbar': self._render_navbar,
        }
        
        renderer = renderers.get(section_type, self._render_placeholder)
        return renderer(props)
    
    def _render_hero_centered(self, props: Dict) -> str:
        return f'''
    <section class="section" style="text-align: center; background: {props.get('backgroundColor', 'var(--color-primary)')}; color: white; padding: 120px 0;">
      <div class="container">
        <h1 style="font-size: 48px; margin-bottom: 16px;">{props.get('title', 'Welcome')}</h1>
        <p style="font-size: 18px; opacity: 0.9; margin-bottom: 32px; max-width: 600px; margin-left: auto; margin-right: auto;">{props.get('subtitle', 'Build something amazing')}</p>
        <a href="#" class="btn" style="background: white; color: {props.get('backgroundColor', 'var(--color-primary)')};">{props.get('ctaText', 'Get Started')}</a>
      </div>
    </section>
'''
    
    def _render_hero_split(self, props: Dict) -> str:
        return f'''
    <section class="section" style="background: {props.get('backgroundColor', 'var(--color-primary)')}; color: white;">
      <div class="container" style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: center;">
        <div>
          <h1 style="font-size: 48px; margin-bottom: 16px;">{props.get('title', 'Welcome')}</h1>
          <p style="font-size: 18px; opacity: 0.9; margin-bottom: 32px;">{props.get('subtitle', 'Build something amazing')}</p>
          <a href="#" class="btn" style="background: white; color: {props.get('backgroundColor', 'var(--color-primary)')};">{props.get('ctaText', 'Get Started')}</a>
        </div>
        <div style="background: rgba(255,255,255,0.1); border-radius: 12px; height: 300px;"></div>
      </div>
    </section>
'''
    
    def _render_features_grid(self, props: Dict) -> str:
        items = props.get('items', [
            {'title': 'Fast', 'description': 'Lightning fast performance', 'icon': '⚡'},
            {'title': 'Secure', 'description': 'Enterprise-grade security', 'icon': '🔒'},
            {'title': 'Scalable', 'description': 'Grows with your business', 'icon': '📈'}
        ])
        
        columns = props.get('columns', 3)
        
        items_html = ''.join([f'''
          <div style="padding: 24px; background: white; border-radius: 12px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <div style="font-size: 32px; margin-bottom: 12px;">{item.get('icon', '✨')}</div>
            <h3 style="font-size: 18px; margin-bottom: 8px;">{item.get('title', 'Feature')}</h3>
            <p style="color: #64748b; font-size: 14px;">{item.get('description', 'Description')}</p>
          </div>
''' for item in items])
        
        return f'''
    <section class="section" style="background: #f8fafc;">
      <div class="container">
        <h2 style="text-align: center; font-size: 36px; margin-bottom: 12px;">{props.get('title', 'Features')}</h2>
        <p style="text-align: center; color: #64748b; margin-bottom: 48px;">{props.get('subtitle', 'Everything you need')}</p>
        <div style="display: grid; grid-template-columns: repeat({columns}, 1fr); gap: 24px;">
          {items_html}
        </div>
      </div>
    </section>
'''
    
    def _render_features_cards(self, props: Dict) -> str:
        return self._render_features_grid(props)
    
    def _render_stats(self, props: Dict) -> str:
        items = props.get('items', [
            {'value': '10K+', 'label': 'Users'},
            {'value': '99.9%', 'label': 'Uptime'},
            {'value': '24/7', 'label': 'Support'}
        ])
        
        items_html = ''.join([f'''
          <div style="text-align: center;">
            <div style="font-size: 36px; font-weight: 800; color: var(--color-primary);">{item.get('value', '0')}</div>
            <div style="color: #64748b; margin-top: 4px;">{item.get('label', 'Stat')}</div>
          </div>
''' for item in items])
        
        return f'''
    <section class="section" style="background: white;">
      <div class="container">
        <div style="display: grid; grid-template-columns: repeat({len(items)}, 1fr); gap: 24px;">
          {items_html}
        </div>
      </div>
    </section>
'''
    
    def _render_pricing(self, props: Dict) -> str:
        tiers = props.get('tiers', [
            {'name': 'Starter', 'price': '$0', 'features': ['1 Project', 'Basic Support']},
            {'name': 'Pro', 'price': '$29', 'features': ['Unlimited Projects', 'Priority Support', 'API Access']},
            {'name': 'Enterprise', 'price': '$99', 'features': ['Everything in Pro', 'Custom Integrations', 'Dedicated Support']}
        ])
        
        tiers_html = ''.join([f'''
          <div style="padding: 32px; border: 2px solid {'var(--color-primary)' if i == 1 else '#e2e8f0'}; border-radius: 12px; text-align: center; {'box-shadow: 0 4px 20px rgba(59,130,246,0.15);' if i == 1 else ''}">
            <h3 style="font-size: 18px; margin-bottom: 8px;">{tier.get('name', 'Plan')}</h3>
            <div style="font-size: 40px; font-weight: 800; margin-bottom: 16px;">{tier.get('price', '$0')}<span style="font-size: 14px; color: #64748b;">/mo</span></div>
            <ul style="list-style: none; padding: 0; margin-bottom: 24px;">
              {''.join([f'<li style="padding: 8px 0; color: #64748b; font-size: 14px;">✓ {feature}</li>' for feature in tier.get('features', [])])}
            </ul>
            <a href="#" class="btn" style="width: 100%; {'background: var(--color-primary);' if i == 1 else 'background: #f8fafc; color: var(--color-text);'}">Get Started</a>
          </div>
''' for i, tier in enumerate(tiers)])
        
        return f'''
    <section class="section" style="background: white;">
      <div class="container">
        <h2 style="text-align: center; font-size: 36px; margin-bottom: 12px;">{props.get('title', 'Pricing')}</h2>
        <p style="text-align: center; color: #64748b; margin-bottom: 48px;">{props.get('subtitle', 'Choose your plan')}</p>
        <div style="display: grid; grid-template-columns: repeat({len(tiers)}, 1fr); gap: 24px; max-width: 900px; margin: 0 auto;">
          {tiers_html}
        </div>
      </div>
    </section>
'''
    
    def _render_cta_simple(self, props: Dict) -> str:
        return f'''
    <section class="section" style="text-align: center; background: {props.get('backgroundColor', 'var(--color-primary)')}; color: white;">
      <div class="container">
        <h2 style="font-size: 36px; margin-bottom: 12px;">{props.get('title', 'Ready to get started?')}</h2>
        <p style="font-size: 18px; opacity: 0.9; margin-bottom: 32px;">{props.get('subtitle', 'Join thousands of users')}</p>
        <a href="#" class="btn" style="background: white; color: {props.get('backgroundColor', 'var(--color-primary)')};">{props.get('buttonText', 'Sign Up Now')}</a>
      </div>
    </section>
'''
    
    def _render_cta_split(self, props: Dict) -> str:
        return self._render_cta_simple(props)
    
    def _render_testimonials(self, props: Dict) -> str:
        items = props.get('items', [
            {'quote': 'This product transformed how we work.', 'author': 'John D.', 'role': 'CEO, TechStart'},
            {'quote': 'Best investment we ever made.', 'author': 'Jane S.', 'role': 'CTO, DesignCo'}
        ])
        
        items_html = ''.join([f'''
          <div style="padding: 32px; background: #f8fafc; border-radius: 12px;">
            <p style="font-size: 16px; font-style: italic; color: #64748b; margin-bottom: 16px;">"{item.get('quote', 'Great!')}"</p>
            <div style="font-weight: 600;">{item.get('author', 'Author')}</div>
            <div style="color: #64748b; font-size: 14px;">{item.get('role', 'Role')}</div>
          </div>
''' for item in items])
        
        return f'''
    <section class="section" style="background: #f8fafc;">
      <div class="container">
        <h2 style="text-align: center; font-size: 36px; margin-bottom: 48px;">{props.get('title', 'What People Say')}</h2>
        <div style="display: grid; grid-template-columns: repeat({len(items)}, 1fr); gap: 24px;">
          {items_html}
        </div>
      </div>
    </section>
'''
    
    def _render_faq(self, props: Dict) -> str:
        questions = props.get('questions', [
            {'q': 'What is this?', 'a': 'A great product.'},
            {'q': 'How much does it cost?', 'a': 'Free for basic plans.'}
        ])
        
        items_html = ''.join([f'''
          <details style="padding: 16px; background: white; border-radius: 8px; margin-bottom: 8px; border: 1px solid #e2e8f0;">
            <summary style="font-weight: 600; cursor: pointer; padding: 8px 0;">{item.get('q', 'Question?')}</summary>
            <p style="color: #64748b; margin-top: 12px; padding: 8px 0;">{item.get('a', 'Answer.')}</p>
          </details>
''' for item in questions])
        
        return f'''
    <section class="section" style="background: #f8fafc;">
      <div class="container" style="max-width: 700px;">
        <h2 style="text-align: center; font-size: 36px; margin-bottom: 48px;">{props.get('title', 'FAQ')}</h2>
        <div>
          {items_html}
        </div>
      </div>
    </section>
'''
    
    def _render_footer(self, props: Dict) -> str:
        links = props.get('links', ['Privacy', 'Terms', 'Contact'])
        links_html = ''.join([f'<a href="#" style="color: #94a3b8; text-decoration: none; margin: 0 12px; font-size: 14px;">{link}</a>' for link in links])
        
        return f'''
    <footer style="padding: 40px 0; background: #0f172a; color: #94a3b8; text-align: center;">
      <div class="container">
        <p style="font-size: 14px;">{props.get('copyright', '© 2024 Your Company')}</p>
        <div style="margin-top: 12px;">
          {links_html}
        </div>
      </div>
    </footer>
'''
    
    def _render_navbar(self, props: Dict) -> str:
        links = props.get('links', ['Home', 'Features', 'Pricing', 'Contact'])
        links_html = ''.join([f'<a href="#" style="color: var(--color-text); text-decoration: none; margin: 0 16px; font-weight: 500;">{link}</a>' for link in links])
        
        return f'''
    <nav style="padding: 16px 0; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border-bottom: 1px solid #e2e8f0; position: sticky; top: 0; z-index: 100;">
      <div class="container" style="display: flex; align-items: center; justify-content: space-between;">
        <a href="#" style="font-size: 20px; font-weight: 800; color: var(--color-primary); text-decoration: none;">{props.get('logo', 'Brand')}</a>
        <div style="display: flex; align-items: center;">
          {links_html}
          <a href="#" class="btn" style="margin-left: 16px;">{props.get('ctaText', 'Get Started')}</a>
        </div>
      </div>
    </nav>
'''
    
    def _render_placeholder(self, props: Dict) -> str:
        return f'''
    <section class="section" style="background: #f8fafc;">
      <div class="container">
        <p style="text-align: center; color: #64748b;">Section placeholder</p>
      </div>
    </section>
'''


class ReactExporter:
    """Export project to React components"""
    
    def __init__(self, project: Dict):
        self.project = project
        self.design = project.get('design', {})
    
    def export(self, output_dir: str) -> str:
        """Export project to React files"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate package.json
        self._write_package_json(output_dir)
        
        # Generate components
        self._write_components(output_dir)
        
        # Generate App.jsx
        self._write_app(output_dir)
        
        # Generate styles
        self._write_styles(output_dir)
        
        return output_dir
    
    def _write_package_json(self, output_dir: str):
        package = {
            "name": self.project['name'].lower().replace(' ', '-'),
            "version": "1.0.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build"
            }
        }
        
        with open(os.path.join(output_dir, 'package.json'), 'w') as f:
            json.dump(package, f, indent=2)
    
    def _write_components(self, output_dir: str):
        components_dir = os.path.join(output_dir, 'src', 'components')
        Path(components_dir).mkdir(parents=True, exist_ok=True)
        
        sections = self.project['pages'][0]['sections']
        
        for i, section in enumerate(sections):
            component_name = f"Section{i:02d}"
            component = self._generate_component(component_name, section)
            
            with open(os.path.join(components_dir, f'{component_name}.jsx'), 'w') as f:
                f.write(component)
    
    def _generate_component(self, name: str, section: Dict) -> str:
        section_type = section['type']
        props = section.get('props', {})
        
        return f'''import React from 'react';

export default function {name}() {{
  return (
    <section className="section" style={{{{ padding: '80px 0' }}}}>
      <div className="container" style={{{{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}}}>
        <h2 style={{{{ fontSize: '36px', textAlign: 'center', marginBottom: '16px' }}}}>{props.get('title', 'Section Title')}</h2>
        <p style={{{{ textAlign: 'center', color: '#64748b' }}}}>{props.get('subtitle', 'Section description')}</p>
      </div>
    </section>
  );
}}
'''
    
    def _write_app(self, output_dir: str):
        sections = self.project['pages'][0]['sections']
        
        imports = '\n'.join([f"import Section{i:02d} from './components/Section{i:02d}';" for i in range(len(sections))])
        components = '\n      '.join([f"<Section{i:02d} />" for i in range(len(sections))])
        
        app = f'''import React from 'react';
{imports}

export default function App() {{
  return (
    <main>
      {components}
    </main>
  );
}}
'''
        
        with open(os.path.join(output_dir, 'src', 'App.jsx'), 'w') as f:
            f.write(app)
        
        # index.jsx
        index = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''
        
        with open(os.path.join(output_dir, 'src', 'index.jsx'), 'w') as f:
            f.write(index)
    
    def _write_styles(self, output_dir: str):
        colors = self.design.get('colors', {})
        
        styles = f''':root {{
  --color-primary: {colors.get('primary', '#3b82f6')};
  --color-secondary: {colors.get('secondary', '#8b5cf6')};
  --color-accent: {colors.get('accent', '#f59e0b')};
  --color-bg: {colors.get('bg', '#ffffff')};
  --color-text: {colors.get('text', '#1e293b')};
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: var(--color-text);
  background: var(--color-bg);
  line-height: 1.6;
}}

.container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}}
'''
        
        with open(os.path.join(output_dir, 'src', 'styles.css'), 'w') as f:
            f.write(styles)


class JSONExporter:
    """Export project to JSON format"""
    
    def __init__(self, project: Dict):
        self.project = project
    
    def export(self, output_path: str) -> str:
        """Export project to JSON file"""
        export_data = {
            'version': ProjectSchema.VERSION,
            'exported_at': datetime.now().isoformat(),
            'project': self.project
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return output_path


class ExportManager:
    """Manage all export formats"""
    
    def __init__(self, project: Dict):
        self.project = project
        self.exporters = {
            'html': HTMLExporter(project),
            'react': ReactExporter(project),
            'json': JSONExporter(project),
        }
    
    def export(self, format: str, output_path: str) -> str:
        """Export project to specified format"""
        if format in self.exporters:
            return self.exporters[format].export(output_path)
        raise ValueError(f"Unsupported format: {format}")
    
    def export_all(self, output_dir: str) -> Dict[str, str]:
        """Export to all formats"""
        results = {}
        
        results['html'] = self.export('html', os.path.join(output_dir, 'index.html'))
        results['react'] = self.export('react', os.path.join(output_dir, 'react'))
        results['json'] = self.export('json', os.path.join(output_dir, 'project.json'))
        
        return results


__all__ = [
    'ProjectSchema', 'HTMLExporter', 'ReactExporter', 'JSONExporter', 'ExportManager'
]
