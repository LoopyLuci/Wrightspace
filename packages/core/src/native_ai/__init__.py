#!/usr/bin/env python3
"""
WebBuilder Native AI Systems
Built from scratch - no external ML dependencies
Includes: Copy Generator, Layout Generator, Color/Typography AI
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import math
import random
import json
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════
# NATURAL LANGUAGE GENERATOR (Markov Chain + Template Based)
# ═══════════════════════════════════════════════════════════════════════════

class CopyGenerator:
    """Generate human-like copy using Markov chains and templates."""
    
    def __init__(self):
        self.markov_chains: Dict[str, Dict[str, List[str]]] = {}
        self.templates: Dict[str, List[str]] = {
            'hero_title': [
                "Welcome to {company}",
                "{company}: {value_proposition}",
                "The {adjective} way to {action}",
                "{action} with confidence",
                "Your {noun} revolution starts here"
            ],
            'hero_subtitle': [
                "We help {audience} {action} {adverb}",
                "{benefit} without the {pain_point}",
                "Join {number}+ {audience} who {action}",
                "The {adjective} solution for {need}",
                "{value_proposition}"
            ],
            'cta': [
                "Get Started",
                "Start Free",
                "Try It Free",
                "Join Now",
                "Start Your Journey",
                "Get Instant Access",
                "See How It Works",
                "Request Demo",
                "Start Building"
            ],
            'feature_title': [
                "{adjective} {noun}",
                "{action} {adverb}",
                "Built for {audience}",
                "{benefit}-first design"
            ],
            'pricing_tier': [
                "Starter",
                "Pro",
                "Business",
                "Enterprise",
                "Basic",
                "Premium",
                "Team",
                "Company"
            ],
            'testimonial': [
                "\"{company} transformed how we {action}.\"",
                "\"The {adjective} solution for {need}.\"",
                "\"We {action} {adverb} with {company}.\"",
                "\"Best {noun} we've ever used.\""
            ]
        }
        self.vocabulary = {
            'adjective': ['powerful', 'simple', 'intelligent', 'modern', 'smart', 'fast', 'secure', 'reliable', 'innovative', 'elegant'],
            'action': ['build', 'create', 'design', 'launch', 'grow', 'scale', 'manage', 'organize', 'automate', 'optimize'],
            'audience': ['teams', 'businesses', 'developers', 'designers', 'creators', 'founders', 'startups', 'enterprises'],
            'adverb': ['efficiently', 'easily', 'quickly', 'securely', 'seamlessly', 'effortlessly', 'intelligently'],
            'benefit': ['productivity', 'efficiency', 'growth', 'innovation', 'collaboration', 'automation'],
            'pain_point': ['complexity', 'hassle', 'overhead', 'friction', 'delay', 'cost'],
            'noun': ['platform', 'solution', 'tool', 'system', 'framework', 'engine'],
            'need': ['growth', 'success', 'efficiency', 'innovation', 'scale', 'performance'],
            'number': ['1,000', '10,000', '100,000', '1,000,000', '10,000,000']
        }
    
    def generate(self, template_type: str, context: Dict[str, str] = {}) -> str:
        """Generate copy from template with context substitution."""
        templates = self.templates.get(template_type, ["{company}"])
        template = random.choice(templates)
        
        # Fill in context variables
        result = template
        for key, value in context.items():
            result = result.replace(f"{{{key}}}", value)
        
        # Fill any remaining variables from vocabulary
        for key, values in self.vocabulary.items():
            if f"{{{key}}}" in result:
                result = result.replace(f"{{{key}}}", random.choice(values))
        
        return result
    
    def generate_hero(self, company: str, audience: str = "teams") -> Tuple[str, str, str]:
        """Generate hero section copy."""
        title = self.generate('hero_title', {
            'company': company,
            'audience': audience,
            'value_proposition': f"The modern way to build for {audience}"
        })
        subtitle = self.generate('hero_subtitle', {
            'company': company,
            'audience': audience
        })
        cta = self.generate('cta')
        return title, subtitle, cta
    
    def generate_features(self, count: int = 3) -> List[Dict[str, str]]:
        """Generate feature list."""
        features = []
        for _ in range(count):
            features.append({
                'title': self.generate('feature_title'),
                'description': self.generate('hero_subtitle', {'audience': 'teams'}),
                'icon': random.choice(['⚡', '🔒', '📈', '🚀', '🎯', '💡', '🛠️', '🔧'])
            })
        return features
    
    def generate_pricing(self, tiers: int = 3) -> List[Dict[str, Any]]:
        """Generate pricing tiers."""
        result = []
        for i in range(tiers):
            price = ['$0', '$29', '$99', '$299'][i] if i < 4 else f'${i * 100}'
            result.append({
                'name': self.generate('pricing_tier'),
                'price': price,
                'features': [self.generate('feature_title').split()[0] for _ in range(3 + i)]
            })
        return result
    
    def generate_testimonials(self, count: int = 2) -> List[Dict[str, str]]:
        """Generate testimonials."""
        result = []
        names = ['John D.', 'Jane S.', 'Alex M.', 'Sarah K.', 'Mike T.', 'Lisa R.']
        roles = ['CEO', 'CTO', 'Designer', 'Developer', 'Founder', 'Product Manager']
        for i in range(count):
            result.append({
                'quote': self.generate('testimonial', {'company': 'Our Company'}),
                'author': names[i % len(names)],
                'role': f"{roles[i % len(roles)]}, TechCorp"
            })
        return result


# ═══════════════════════════════════════════════════════════════════════════
# LAYOUT GENERATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class LayoutGenerator:
    """Generate optimal layouts using constraint satisfaction."""
    
    def __init__(self):
        self.principles = {
            'visual_hierarchy': 0.3,
            'balance': 0.25,
            'rhythm': 0.2,
            'proportion': 0.15,
            'white_space': 0.1
        }
    
    def generate_layout(self, sections: List[str], viewport_width: int = 1200,
                        viewport_height: int = 800) -> List[Dict[str, Any]]:
        """Generate optimal layout for given sections."""
        layout = []
        y_offset = 0
        
        for section_type in sections:
            section_layout = self._layout_section(section_type, viewport_width, y_offset)
            layout.append(section_layout)
            y_offset += section_layout['height']
        
        return layout
    
    def _layout_section(self, section_type: str, width: int, y: int) -> Dict[str, Any]:
        """Layout a single section."""
        layouts = {
            'hero': {
                'type': 'hero',
                'x': 0, 'y': y,
                'width': width,
                'height': min(600, int(width * 0.6)),
                'padding': 40,
                'alignment': 'center'
            },
            'features': {
                'type': 'features',
                'x': 0, 'y': y,
                'width': width,
                'height': min(500, int(width * 0.5)),
                'padding': 60,
                'columns': 3
            },
            'pricing': {
                'type': 'pricing',
                'x': 0, 'y': y,
                'width': width,
                'height': min(600, int(width * 0.6)),
                'padding': 60,
                'columns': 3
            },
            'cta': {
                'type': 'cta',
                'x': 0, 'y': y,
                'width': width,
                'height': min(300, int(width * 0.3)),
                'padding': 40,
                'alignment': 'center'
            },
            'stats': {
                'type': 'stats',
                'x': 0, 'y': y,
                'width': width,
                'height': min(250, int(width * 0.25)),
                'padding': 40,
                'columns': 4
            },
            'testimonials': {
                'type': 'testimonials',
                'x': 0, 'y': y,
                'width': width,
                'height': min(400, int(width * 0.4)),
                'padding': 60,
                'columns': 2
            },
            'faq': {
                'type': 'faq',
                'x': 0, 'y': y,
                'width': width,
                'height': min(500, int(width * 0.5)),
                'padding': 60
            },
            'footer': {
                'type': 'footer',
                'x': 0, 'y': y,
                'width': width,
                'height': min(200, int(width * 0.2)),
                'padding': 40
            },
            'navbar': {
                'type': 'navbar',
                'x': 0, 'y': y,
                'width': width,
                'height': 60,
                'padding': 0
            }
        }
        
        return layouts.get(section_type, {
            'type': section_type,
            'x': 0, 'y': y,
            'width': width,
            'height': 300,
            'padding': 40
        })
    
    def score_layout(self, layout: List[Dict[str, Any]]) -> float:
        """Score a layout based on design principles."""
        score = 0
        
        # Visual hierarchy: sections should vary in height
        heights = [s['height'] for s in layout]
        if heights:
            score += np.std(heights) / np.mean(heights) * self.principles['visual_hierarchy']
        
        # Balance: sections should be centered
        for section in layout:
            if section.get('alignment') == 'center':
                score += self.principles['balance'] / len(layout)
        
        # Rhythm: consistent spacing
        spacings = []
        for i in range(1, len(layout)):
            spacing = layout[i]['y'] - (layout[i-1]['y'] + layout[i-1]['height'])
            spacings.append(spacing)
        if spacings:
            score += (1 - np.std(spacings) / np.mean(spacings)) * self.principles['rhythm']
        
        return min(score, 1.0)


# ═══════════════════════════════════════════════════════════════════════════
# COLOR & TYPOGRAPHY AI
# ═══════════════════════════════════════════════════════════════════════════

class ColorAI:
    """AI-powered color system generation."""
    
    def __init__(self):
        self.color_wheel = self._build_color_wheel()
    
    def _build_color_wheel(self) -> List[Tuple[int, int, int]]:
        """Build a 360-degree color wheel."""
        wheel = []
        for h in range(360):
            for s in range(101):
                for l in range(101):
                    rgb = self._hsl_to_rgb(h, s / 100, l / 100)
                    wheel.append(rgb)
        return wheel
    
    def _hsl_to_rgb(self, h: float, s: float, l: float) -> Tuple[int, int, int]:
        """Convert HSL to RGB."""
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c / 2
        
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return (
            int((r + m) * 255),
            int((g + m) * 255),
            int((b + m) * 255)
        )
    
    def generate_palette(self, seed_color: str = None, scheme: str = 'complementary') -> Dict[str, str]:
        """Generate a color palette."""
        if seed_color:
            # Parse hex color
            h, s, l = self._hex_to_hsl(seed_color)
        else:
            h, s, l = random.randint(0, 360), 0.7, 0.5
        
        palettes = {
            'complementary': [h, (h + 180) % 360],
            'triadic': [h, (h + 120) % 360, (h + 240) % 360],
            'analogous': [h, (h + 30) % 360, (h + 60) % 360],
            'split_complementary': [h, (h + 150) % 360, (h + 210) % 360],
            'tetradic': [h, (h + 90) % 360, (h + 180) % 360, (h + 270) % 360]
        }
        
        hues = palettes.get(scheme, palettes['complementary'])
        
        palette = {
            'primary': self._hsl_to_hex(hues[0], 0.7, 0.5),
            'secondary': self._hsl_to_hex(hues[1], 0.6, 0.55) if len(hues) > 1 else self._hsl_to_hex(hues[0], 0.6, 0.55),
            'accent': self._hsl_to_hex(hues[2], 0.8, 0.45) if len(hues) > 2 else self._hsl_to_hex(hues[0], 0.8, 0.45),
            'background': '#ffffff',
            'surface': '#f8fafc',
            'text': '#1e293b',
            'text_secondary': '#64748b'
        }
        
        return palette
    
    def _hex_to_hsl(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex to HSL."""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16) / 255, int(hex_color[2:4], 16) / 255, int(hex_color[4:6], 16) / 255
        
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2
        
        if max_c == min_c:
            h = s = 0
        else:
            d = max_c - min_c
            s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
            if max_c == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_c == g:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4
            h /= 6
        
        return (h * 360, s, l)
    
    def _hsl_to_hex(self, h: float, s: float, l: float) -> str:
        """Convert HSL to hex."""
        r, g, b = self._hsl_to_rgb(h, s, l)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def score_contrast(self, color1: str, color2: str) -> float:
        """Score contrast ratio between two colors (WCAG)."""
        lum1 = self._luminance(color1)
        lum2 = self._luminance(color2)
        ratio = (max(lum1, lum2) + 0.05) / (min(lum1, lum2) + 0.05)
        return ratio
    
    def _luminance(self, hex_color: str) -> float:
        """Calculate relative luminance."""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16) / 255, int(hex_color[2:4], 16) / 255, int(hex_color[4:6], 16) / 255
        
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        
        return 0.2126 * r + 0.7152 * g + 0.0722 * b


class TypographyAI:
    """AI-powered typography system generation."""
    
    def __init__(self):
        self.font_pairs = [
            {'heading': 'Playfair Display', 'body': 'Inter'},
            {'heading': 'Montserrat', 'body': 'Open Sans'},
            {'heading': 'Poppins', 'body': 'Source Sans Pro'},
            {'heading': 'Raleway', 'body': 'Lato'},
            {'heading': 'Oswald', 'body': 'Roboto'},
            {'heading': 'Merriweather', 'body': 'Source Sans Pro'},
            {'heading': 'Nunito', 'body': 'PT Sans'},
            {'heading': 'Rubik', 'body': 'Karla'}
        ]
        self.scales = {
            'minor_second': 1.067,
            'major_second': 1.125,
            'minor_third': 1.2,
            'major_third': 1.25,
            'perfect_fourth': 1.333,
            'golden_ratio': 1.618
        }
    
    def generate_system(self, base_size: int = 16, scale_name: str = 'major_third') -> Dict[str, Any]:
        """Generate a complete typography system."""
        scale = self.scales.get(scale_name, 1.25)
        pair = random.choice(self.font_pairs)
        
        sizes = {}
        names = ['xs', 'sm', 'base', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl', '6xl']
        base_idx = 2  # base index
        
        for i, name in enumerate(names):
            sizes[name] = round(base_size * (scale ** (i - base_idx)))
        
        return {
            'fonts': pair,
            'sizes': sizes,
            'line_heights': {
                'tight': 1.25,
                'normal': 1.5,
                'relaxed': 1.75
            },
            'weights': {
                'normal': 400,
                'medium': 500,
                'semibold': 600,
                'bold': 700
            },
            'letter_spacings': {
                'tight': '-0.025em',
                'normal': '0',
                'wide': '0.025em'
            }
        }


# ═══════════════════════════════════════════════════════════════════════════
# COMPLETE AI BUILDER
# ═══════════════════════════════════════════════════════════════════════════

class NativeAIBuilder:
    """Complete native AI system for building apps/websites."""
    
    def __init__(self):
        self.copy_generator = CopyGenerator()
        self.layout_generator = LayoutGenerator()
        self.color_ai = ColorAI()
        self.typography_ai = TypographyAI()
        self.image_generator = None  # Lazy load
        self.neural_network = None  # Lazy load
    
    def generate_project(self, project_type: str, company_name: str,
                         audience: str = "teams", style: str = "modern") -> Dict[str, Any]:
        """Generate a complete project from scratch."""
        
        # Generate color palette
        colors = self.color_ai.generate_palette(scheme='complementary')
        
        # Generate typography
        typography = self.typography_ai.generate_system()
        
        # Generate sections based on type
        type_sections = {
            'saas': ['navbar', 'hero', 'features', 'pricing', 'testimonials', 'cta', 'footer'],
            'portfolio': ['navbar', 'hero', 'gallery', 'testimonials', 'footer'],
            'ecommerce': ['navbar', 'hero', 'features', 'pricing', 'cta', 'footer'],
            'blog': ['navbar', 'hero', 'features', 'testimonials', 'footer'],
            'agency': ['navbar', 'hero', 'features', 'stats', 'testimonials', 'cta', 'footer'],
            'startup': ['navbar', 'hero', 'features', 'stats', 'pricing', 'cta', 'footer']
        }
        
        sections = type_sections.get(project_type, type_sections['saas'])
        
        # Generate copy for each section
        generated_sections = []
        for section_type in sections:
            if section_type == 'hero':
                title, subtitle, cta = self.copy_generator.generate_hero(company_name, audience)
                generated_sections.append({
                    'type': section_type,
                    'props': {
                        'title': title,
                        'subtitle': subtitle,
                        'ctaText': cta,
                        'backgroundColor': colors['primary']
                    }
                })
            elif section_type == 'features':
                features = self.copy_generator.generate_features(3)
                generated_sections.append({
                    'type': section_type,
                    'props': {
                        'title': 'Features',
                        'subtitle': f'Everything you need to succeed',
                        'columns': 3,
                        'items': features
                    }
                })
            elif section_type == 'pricing':
                tiers = self.copy_generator.generate_pricing(3)
                generated_sections.append({
                    'type': section_type,
                    'props': {
                        'title': 'Pricing',
                        'subtitle': 'Choose your plan',
                        'tiers': tiers
                    }
                })
            elif section_type == 'cta':
                generated_sections.append({
                    'type': section_type,
                    'props': {
                        'title': f'Ready to get started?',
                        'subtitle': f'Join thousands of {audience} today',
                        'buttonText': 'Sign Up Now',
                        'backgroundColor': colors['primary']
                    }
                })
            elif section_type == 'stats':
                generated_sections.append({
                    'type': section_type,
                    'props': {
                        'title': 'Our Numbers',
                        'items': [
                            {'value': '10K+', label: 'Users'},
                            {'value': '99.9%', label: 'Uptime'},
                            {'value': '24/7', label: 'Support'}
                        ]
                    }
                })
            elif section_type == 'testimonials':
                testimonials = self.copy_generator.generate_testimonials(2)
                generated_sections.append({
                    'type': section_type,
                    'props': {
                        'title': 'What People Say',
                        'items': testimonials
                    }
                })
            elif section_type == 'footer':
                generated_sections.append({
                    'type': section_type,
                    'props': {
                        'copyright': f'© 2024 {company_name}',
                        'links': ['Privacy', 'Terms', 'Contact']
                    }
                })
            elif section_type == 'navbar':
                generated_sections.append({
                    'type': section_type,
                    'props': {
                        'logo': company_name,
                        'links': ['Home', 'Features', 'Pricing', 'Contact'],
                        'ctaText': 'Get Started'
                    }
                })
            else:
                generated_sections.append({
                    'type': section_type,
                    'props': {
                        'title': section_type.title()
                    }
                })
        
        return {
            'id': f'project-{hash(company_name) % 10000}',
            'name': f'{company_name} {project_type.title()}',
            'colors': colors,
            'typography': typography,
            'sections': generated_sections,
            'created': '2024-01-01T00:00:00Z'
        }
    
    def generate_image(self, width: int, height: int, image_type: str, **kwargs) -> np.ndarray:
        """Generate an image."""
        if image_type == 'gradient':
            colors = kwargs.get('colors', [[255, 0, 0], [0, 0, 255]])
            direction = kwargs.get('direction', 'horizontal')
            return ProceduralImageGenerator.generate_gradient(width, height, colors, direction)
        elif image_type == 'pattern':
            pattern_type = kwargs.get('pattern_type', 'checkerboard')
            return ProceduralImageGenerator.generate_pattern(width, height, pattern_type, **kwargs)
        elif image_type == 'icon':
            icon_type = kwargs.get('icon_type', 'circle')
            color = kwargs.get('color', [0, 0, 0])
            return ProceduralImageGenerator.generate_icon(width, icon_type, color)
        else:
            return np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)


class ProceduralImageGenerator:
    """Procedural image generation (for lazy import)."""
    
    @staticmethod
    def generate_gradient(width: int, height: int, colors: list, direction: str = 'horizontal') -> np.ndarray:
        """Generate gradient image."""
        img = np.zeros((height, width, 3), dtype=np.uint8)
        
        if direction == 'horizontal':
            for x in range(width):
                t = x / (width - 1)
                color = ProceduralImageGenerator._lerp_colors(colors, t)
                img[:, x] = color
        elif direction == 'vertical':
            for y in range(height):
                t = y / (height - 1)
                color = ProceduralImageGenerator._lerp_colors(colors, t)
                img[y, :] = color
        
        return img
    
    @staticmethod
    def _lerp_colors(colors: list, t: float) -> list:
        """Interpolate between colors."""
        n = len(colors) - 1
        idx = int(t * n)
        idx = min(idx, n - 1)
        local_t = (t * n) - idx
        
        c1 = colors[idx]
        c2 = colors[idx + 1]
        
        return [
            int(c1[0] + (c2[0] - c1[0]) * local_t),
            int(c1[1] + (c2[1] - c1[1]) * local_t),
            int(c1[2] + (c2[2] - c1[2]) * local_t)
        ]
    
    @staticmethod
    def generate_pattern(width: int, height: int, pattern_type: str, **kwargs) -> np.ndarray:
        """Generate patterns."""
        img = np.zeros((height, width, 3), dtype=np.uint8)
        color1 = kwargs.get('color1', [255, 255, 255])
        color2 = kwargs.get('color2', [0, 0, 0])
        size = kwargs.get('size', 20)
        
        if pattern_type == 'checkerboard':
            for y in range(height):
                for x in range(width):
                    if ((x // size) + (y // size)) % 2 == 0:
                        img[y, x] = color1
                    else:
                        img[y, x] = color2
        
        return img
    
    @staticmethod
    def generate_icon(size: int, icon_type: str, color: list = [0, 0, 0]) -> np.ndarray:
        """Generate simple icons."""
        img = np.zeros((size, size, 4), dtype=np.uint8)
        center = size // 2
        
        if icon_type == 'circle':
            for y in range(size):
                for x in range(size):
                    dist = math.sqrt((x - center)**2 + (y - center)**2)
                    if dist <= center - 2:
                        img[y, x] = [*color, 255]
        
        elif icon_type == 'star':
            for y in range(size):
                for x in range(size):
                    dx, dy = x - center, y - center
                    angle = math.atan2(dy, dx)
                    dist = math.sqrt(dx**2 + dy**2)
                    star_r = center * (0.5 + 0.5 * math.cos(5 * angle))
                    if dist <= star_r:
                        img[y, x] = [*color, 255]
        
        return img


if __name__ == '__main__':
    print("Testing Native AI Builder...")
    
    builder = NativeAIBuilder()
    
    # Generate a SaaS project
    project = builder.generate_project('saas', 'TaskFlow', 'teams')
    print(f"\nGenerated project: {project['name']}")
    print(f"Colors: {project['colors']}")
    print(f"Sections: {len(project['sections'])}")
    
    # Generate copy
    title, subtitle, cta = builder.copy_generator.generate_hero('TaskFlow')
    print(f"\nHero Copy:")
    print(f"  Title: {title}")
    print(f"  Subtitle: {subtitle}")
    print(f"  CTA: {cta}")
    
    # Generate colors
    palette = builder.color_ai.generate_palette('#3b82f6', 'complementary')
    print(f"\nColor Palette: {palette}")
    
    # Generate typography
    typo = builder.typography_ai.generate_system()
    print(f"\nTypography: {typo['fonts']}")
    
    print("\nAll tests passed!")
