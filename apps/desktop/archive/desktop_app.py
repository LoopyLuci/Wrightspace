#!/usr/bin/env python3
"""
WebBuilder Desktop v6.0 — Premium Edition
Qt fix applied, no properties panel, dedicated settings, real models
"""

import sys
import os
import sys
import json
import math
import random
import numpy as np
from pathlib import Path
from datetime import datetime
from threading import Thread

import os
os.environ['QT_OPENGL_TYPE'] = 'software'
os.environ['QT_OPENGL'] = 'software'

from PyQt5.QtCore import Qt, QCoreApplication
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

# ═══════════════════════════════════════════════════════════════════════════
# PREMIUM STYLESHEET
# ═══════════════════════════════════════════════════════════════════════════

STYLESHEET = """
/* ===== Global ===== */
* {
    font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-weight: 400;
}

QMainWindow {
    background: #0a0a0f;
    color: #e2e8f0;
}

/* ===== Tabs ===== */
QTabBar {
    font-weight: 600;
    font-size: 13px;
}

QTabBar::tab {
    padding: 14px 24px;
    background: transparent;
    color: #64748b;
    border: none;
    border-bottom: 2px solid transparent;
}

QTabBar::tab:selected {
    color: #3b82f6;
    border-bottom: 2px solid #3b82f6;
    background: rgba(59, 130, 246, 0.08);
}

QTabWidget::pane {
    background: #0a0a0f;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}

/* ===== Toolbar ===== */
QToolBar {
    background: rgba(30, 30, 44, 0.95);
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding: 6px 12px;
    spacing: 12px;
}

QToolButton {
    background: rgba(255, 255, 255, 0.06);
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 12px;
}

QToolButton:hover {
    background: rgba(255, 255, 255, 0.12);
}

QToolButton[primary="true"] {
    background: #3b82f6;
    color: white;
    border-color: #3b82f6;
    box-shadow: 0 4px 12px rgba(59,130,246,0.3);
}

QToolButton[primary="true"]:hover {
    background: #2563eb;
}

/* ===== Buttons ===== */
QPushButton {
    background: rgba(255, 255, 255, 0.06);
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 8px 16px;
}

QPushButton:hover {
    background: rgba(255, 255, 255, 0.12);
}

QPushButton[primary="true"] {
    background: #3b82f6;
    color: white;
    border: none;
}

QPushButton[primary="true"]:hover {
    background: #2563eb;
}

QPushButton[pushContent="true"] {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 14px;
    border-radius: 10px;
}

/* ===== Inputs ===== */
QLineEdit, QComboBox, QSpinBox, QTextEdit {
    background: rgba(15, 23, 42, 0.4);
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
}

QLineEdit:focus {
    border-color: #3b82f6;
}

QComboBox {
    padding: 6px 12px;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background: #1e293b;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
}

/* ===== Checkboxes ===== */
QCheckBox {
    color: #e2e8f0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
}

QCheckBox::indicator:checked {
    background: #3b82f6;
}

/* ===== Status Bar ===== */
QStatusBar {
    background: rgba(15, 23, 42, 0.9);
    color: #64748b;
    font-size: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
}

/* ===== Menu Bar ===== */
QMenuBar {
    background: rgba(20, 20, 34, 0.95);
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    color: #e2e8f0;
}

QMenuBar::item:selected {
    background: rgba(255, 255, 255, 0.08);
}

QMenu {
    background: #1e293b;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
}

QMenu::item:selected {
    background: rgba(59, 130, 246, 0.15);
}

/* ===== WebEngine ===== */
QWebEngineView {
    border: none;
}

/* ===== Panels ===== */
QFrame {
    background: transparent;
}
"""

# ═══════════════════════════════════════════════════════════════════════════
# SECTION DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

SECTIONS = {
    'Navbar': {
        'icon': '🔍',
        'props_template': {
            'logo': 'WebBuilder',
            'links': ['Home', 'About', 'Contact'],
            'ctaText': 'Get Started',
            'ctaLink': '#',
        }
    },
    'Hero — Centered': {
        'icon': '🎯',
        'props_template': {
            'type': 'centered',
            'title': 'Build Something Amazing',
            'subtitle': 'The professional way to create beautiful websites and applications',
            'ctaText': 'Get Started',
            'ctaColor': '#3b82f6',
        }
    },
    'Hero — Split Left': {
        'icon': '✂️',
        'props_template': {
            'type': 'split',
            'title': 'Transform Your Business',
            'subtitle': 'Join thousands of satisfied customers',
            'ctaText': 'Start Free Trial',
            'ctaColor': '#1e293b',
            'image': 'https://picsum.photos/seed/demo/800/600',
        }
    },
    'Hero — Minimal': {
        'icon': '🎨',
        'props_template': {
            'type': 'minimal',
            'title': 'Simple. Clean. Powerful.',
            'subtitle': 'Beautiful design meets powerful functionality',
            'ctaText': 'Learn More',
        }
    },
    'Features — 3 Columns': {
        'icon': '🔲',
        'props_template': {
            'columns': 3,
            'title': 'Features',
            'subtitle': 'Everything you need to succeed',
            'items': [
                {'icon': '⚡', 'title': 'Lightning Fast', 'description': 'Optimized for performance with sub-second load times'},
                {'icon': '🔒', 'title': 'Enterprise Security', 'description': 'Bank-grade encryption and SOC2 compliance'},
                {'icon': '🌍', 'title': 'Global Scale', 'description': 'Deploy anywhere — AWS, GCP, Azure, or your own servers'},
            ]
        }
    },
    'Features — 4 Columns': {
        'icon': '🔳',
        'props_template': {
            'columns': 4,
            'title': 'Features',
            'subtitle': 'Comprehensive feature set',
            'items': [
                {'icon': '⚡', 'title': 'Speed', 'description': 'Optimized for performance'},
                {'icon': '🔒', 'title': 'Security', 'description': 'Enterprise-grade'},
                {'icon': '🌍', 'title': 'Scale', 'description': 'Global deployment'},
                {'icon': '💎', 'title': 'Quality', 'description': 'Mission-critical'},
            ]
        }
    },
    'Features — Cards': {
        'icon': '💳',
        'props_template': {
            'title': 'Why Choose Us',
            'subtitle': 'Built for modern teams',
            'items': [
                {'icon': '🎨', 'title': 'Beautiful Design', 'description': 'Stunning templates crafted by top designers'},
                {'icon': '⚡', 'title': 'Lightning Fast', 'description': 'Optimized performance for better UX'},
                {'icon': '🔌', 'title': 'Easy Integration', 'description': 'Connect with your favorite tools'},
            ]
        }
    },
    'CTA — Simple': {
        'icon': '📣',
        'props_template': {
            'title': 'Ready to Get Started?',
            'subtitle': 'Join thousands of satisfied customers',
            'buttonText': 'Get Started',
            'buttonColor': '#3b82f6',
            'backgroundColor': '#3b82f6',
            'textColor': '#ffffff',
        }
    },
    'CTA — Split': {
        'icon': '🔀',
        'props_template': {
            'title': 'Transform Your Workflow',
            'subtitle': 'Join thousands of satisfied customers',
            'buttonText': 'Start Free Trial',
            'buttonColor': '#1e293b',
            'backgroundColor': '#1e293b',
            'textColor': '#ffffff',
            'image': 'https://picsum.photos/seed/demo2/800/600',
        }
    },
    'Pricing — 3 Tiers': {
        'icon': '💰',
        'props_template': {
            'title': 'Simple, Transparent Pricing',
            'subtitle': 'Choose the plan that fits your needs',
            'highlightTier': 1,
            'tiers': [
                {'name': 'Starter', 'price': '$29/mo', 'description': 'For individuals and small teams', 'features': ['5 projects', 'Basic support', '1GB storage', 'Email only'], 'popular': False},
                {'name': 'Pro', 'price': '$99/mo', 'description': 'For growing businesses', 'features': ['Unlimited projects', 'Priority support', '10GB storage', 'Phone support', 'Advanced analytics', 'API access'], 'popular': True},
                {'name': 'Enterprise', 'price': '$299/mo', 'description': 'For large organizations', 'features': ['Everything in Pro', 'Dedicated account manager', 'Unlimited storage', '24/7 phone support', 'Custom integrations', 'SLA guarantee', 'On-premise option'], 'popular': False},
            ]
        }
    },
    'Pricing — 2 Tiers': {
        'icon': '💸',
        'props_template': {
            'title': 'Simple Pricing',
            'subtitle': 'No hidden fees',
            'highlightTier': 1,
            'tiers': [
                {'name': 'Basic', 'price': '$19/mo', 'description': 'For personal use', 'features': ['3 projects', 'Email support', '500MB storage'], 'popular': False},
                {'name': 'Pro', 'price': '$79/mo', 'description': 'For professionals', 'features': ['Unlimited projects', 'Priority support', '5GB storage', 'Advanced analytics', 'API access'], 'popular': True},
            ]
        }
    },
    'Stats': {
        'icon': '📊',
        'props_template': {
            'title': 'Trusted Worldwide',
            'subtitle': 'Numbers speak for themselves',
            'items': [
                {'value': '10K+', 'label': 'Active Users'},
                {'value': '500+', 'label': 'Enterprise Clients'},
                {'value': '99.9%', 'label': 'Uptime'},
            ],
            'styles': [
                {'color': '#3b82f6', 'suffix': ''},
                {'color': '#8b5cf6', 'suffix': ''},
                {'color': '#f59e0b', 'suffix': ''},
            ]
        }
    },
    'Testimonials — 2 Columns': {
        'icon': '💬',
        'props_template': {
            'title': 'What Our Customers Say',
            'subtitle': 'Real feedback from real users',
            'items': [
                {'quote': 'This product completely transformed how we build websites. The speed and quality are unmatched.', 'author': 'Sarah Johnson', 'role': 'CEO, TechCorp'},
                {'quote': 'The best investment we made this year. Customer support is exceptional.', 'author': 'Michael Chen', 'role': 'Founder, StartupX'},
                {'quote': 'Finally, a tool that just works. No more wrestling with templates.', 'author': 'Emma Williams', 'role': 'Lead Designer, Agency'},
            ]
        }
    },
    'Testimonials — 3 Columns': {
        'icon': '🗣️',
        'props_template': {
            'title': 'Customer Stories',
            'subtitle': 'Hear from our community',
            'items': [
                {'quote': 'Amazing product!', 'author': 'Sarah', 'role': 'CEO'},
                {'quote': 'Great tool!', 'author': 'Mike', 'role': 'Founder'},
                {'quote': 'Highly recommend!', 'author': 'Emma', 'role': 'Designer'},
            ]
        }
    },
    'FAQ': {
        'icon': '❓',
        'props_template': {
            'title': 'Frequently Asked Questions',
            'subtitle': 'Everything you need to know',
            'questions': [
                {'q': 'How do I get started?', 'a': 'Simply sign up for a free account and start building. No credit card required.'},
                {'q': 'Can I upgrade later?', 'a': 'Absolutely! You can upgrade or downgrade at any time. Changes take effect immediately.'},
                {'q': 'Is there a free trial?', 'a': 'Yes, we offer a 14-day free trial with full access to all features.'},
                {'q': 'What payment methods do you accept?', 'a': 'We accept Visa, Mastercard, American Express, and PayPal.'},
            ]
        }
    },
    'Footer': {
        'icon': '📎',
        'props_template': {
            'copyright': '© 2024 WebBuilder. All rights reserved.',
            'links': [
                {'text': 'Privacy Policy', 'url': '#privacy'},
                {'text': 'Terms of Service', 'url': '#terms'},
                {'text': 'Contact', 'url': '#contact'},
            ],
            'social': [
                {'icon': '🐦', 'label': 'Twitter'},
                {'icon': '📘', 'label': 'Facebook'},
                {'icon': '📸', 'label': 'Instagram'},
            ]
        }
    },
}

STYLE_PRESETS = {
    'SaaS': {'colors': {'primary': '#3b82f6', 'secondary': '#8b5cf6', 'accent': '#f59e0b', 'bg': '#ffffff', 'text': '#1e293b'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}},
    'Creative': {'colors': {'primary': '#ec4899', 'secondary': '#8b5cf6', 'accent': '#f59e0b', 'bg': '#ffffff', 'text': '#1e293b'}, 'fonts': {'heading': 'Poppins', 'body': 'Inter'}},
    'Minimal': {'colors': {'primary': '#000000', 'secondary': '#737373', 'accent': '#3b82f6', 'bg': '#ffffff', 'text': '#1e293b'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}},
    'Modern': {'colors': {'primary': '#06b6d4', 'secondary': '#8b5cf6', 'accent': '#f59e0b', 'bg': '#0f172a', 'text': '#f8fafc'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}},
    'Dark': {'colors': {'primary': '#3b82f6', 'secondary': '#8b5cf6', 'accent': '#f59e0b', 'bg': '#0f172a', 'text': '#f8fafc'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}},
    'Corporate': {'colors': {'primary': '#1e40af', 'secondary': '#3730a3', 'accent': '#f59e0b', 'bg': '#ffffff', 'text': '#1e293b'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}},
}

# ═══════════════════════════════════════════════════════════════════════════
# PROVIDER CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

class Config:
    """Configuration: providers, models, sections, styles."""
    
    ALL_PROVIDERS = {
        'openai': {
            'name': 'OpenAI',
            'icon': '🤖',
            'type': 'cloud',
            'endpoint': 'https://api.openai.com/v1/chat/completions',
            'models': [
                {'id': 'gpt-4o', 'name': 'GPT-4o', 'context': 128000, 'free': False},
                {'id': 'gpt-4o-mini', 'name': 'GPT-4o-Mini', 'context': 128000, 'free': False},
                {'id': 'gpt-4-turbo', 'name': 'GPT-4-Turbo', 'context': 128000, 'free': False},
                {'id': 'gpt-4', 'name': 'GPT-4', 'context': 8192, 'free': False},
                {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5-Turbo', 'context': 16385, 'free': False},
            ],
        },
        'anthropic': {
            'name': 'Anthropic',
            'icon': '🧠',
            'type': 'cloud',
            'endpoint': 'https://api.anthropic.com/v1/messages',
            'models': [
                {'id': 'claude-3-5-sonnet-20241022', 'name': 'Claude 3.5 Sonnet', 'context': 200000, 'free': False},
                {'id': 'claude-3-5-haiku-20241022', 'name': 'Claude 3.5 Haiku', 'context': 200000, 'free': False},
                {'id': 'claude-3-opus-20240229', 'name': 'Claude 3 Opus', 'context': 200000, 'free': False},
                {'id': 'claude-3-sonnet-20240229', 'name': 'Claude 3 Sonnet', 'context': 200000, 'free': False},
                {'id': 'claude-3-haiku-20240307', 'name': 'Claude 3 Haiku', 'context': 200000, 'free': False},
            ],
        },
        'google': {
            'name': 'Google Gemini',
            'icon': '🔮',
            'type': 'cloud',
            'endpoint': 'https://generativelanguage.googleapis.com/v1beta',
            'models': [
                {'id': 'gemini-2.0-flash', 'name': 'Gemini 2.0 Flash', 'context': 1000000, 'free': True},
                {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'context': 2000000, 'free': False},
                {'id': 'gemini-1.5-flash', 'name': 'Gemini 1.5 Flash', 'context': 1000000, 'free': False},
                {'id': 'gemini-2.0-flash-lite', 'name': 'Gemini 2.0 Flash-Lite', 'context': 1000000, 'free': True},
            ],
        },
        'openrouter': {
            'name': 'OpenRouter',
            'icon': '🔀',
            'type': 'cloud',
            'endpoint': 'https://openrouter.ai/api/v1/chat/completions',
            'models': [
                {'id': 'openrouter/auto', 'name': 'OpenRouter Auto', 'context': 128000, 'free': False},
                {'id': 'openai/gpt-4o', 'name': 'GPT-4o via OpenRouter', 'context': 128000, 'free': False},
                {'id': 'anthropic/claude-3.5-sonnet', 'name': 'Claude 3.5 Sonnet via OR', 'context': 200000, 'free': False},
                {'id': 'google/gemini-2.0-flash', 'name': 'Gemini 2.0 Flash via OR', 'context': 1000000, 'free': False},
                {'id': 'meta-llama/llama-3.1-405b', 'name': 'Llama 3.1 405B via OR', 'context': 128000, 'free': False},
            ],
        },
        'opencode_go': {
            'name': 'OpenCode Go',
            'icon': '🐹',
            'type': 'cloud',
            'endpoint': 'https://api.opencode.ai/v1/chat/completions',
            'models': [
                {'id': 'opencode-go-default', 'name': 'OpenCode Go Default', 'context': 128000, 'free': False},
                {'id': 'opencode-go-pro', 'name': 'OpenCode Go Pro', 'context': 128000, 'free': False},
            ],
        },
        'opencode_zen': {
            'name': 'OpenCode Zen',
            'icon': '🧘',
            'type': 'cloud',
            'endpoint': 'https://api.opencode.ai/zen/v1/chat/completions',
            'models': [
                {'id': 'opencode-zen-default', 'name': 'OpenCode Zen Default', 'context': 128000, 'free': False},
            ],
        },
        'grok': {
            'name': 'xAI Grok',
            'icon': '🐱',
            'type': 'cloud',
            'endpoint': 'https://api.x.ai/v1/chat/completions',
            'models': [
                {'id': 'grok-3', 'name': 'Grok-3', 'context': 131072, 'free': False},
                {'id': 'grok-3-mini', 'name': 'Grok-3 Mini', 'context': 131072, 'free': False},
                {'id': 'grok-2', 'name': 'Grok-2', 'context': 131072, 'free': False},
                {'id': 'grok-2-mini', 'name': 'Grok-2 Mini', 'context': 131072, 'free': False},
            ],
        },
        'custom_cloud': {
            'name': 'Custom (Cloud)',
            'icon': '⚙️',
            'type': 'cloud',
            'endpoint': 'https://api.example.com/v1/chat/completions',
            'models': [
                {'id': 'custom-endpoint', 'name': 'Custom Endpoint', 'context': 128000, 'free': False},
            ],
        },
        'ollama': {
            'name': 'Ollama',
            'icon': '🦙',
            'type': 'local',
            'endpoint': 'http://localhost:11434/api/chat',
            'models': [
                {'id': 'llama3.2', 'name': 'Llama 3.2', 'context': 32768, 'free': True},
                {'id': 'llama3.1:70b', 'name': 'Llama 3.1 70B', 'context': 131072, 'free': True},
                {'id': 'llama3.1:8b', 'name': 'Llama 3.1 8B', 'context': 128000, 'free': True},
                {'id': 'mistral:7b', 'name': 'Mistral 7B', 'context': 32768, 'free': True},
                {'id': 'gemma2:27b', 'name': 'Gemma 2 27B', 'context': 8192, 'free': True},
                {'id': 'phi3.5:mini', 'name': 'Phi 3.5 Mini', 'context': 128000, 'free': True},
                {'id': 'qwen2.5:7b', 'name': 'Qwen 2.5 7B', 'context': 32768, 'free': True},
                {'id': 'deepseek-r1', 'name': 'DeepSeek-R1', 'context': 128000, 'free': True},
            ],
        },
        'unsloth': {
            'name': 'Unsloth',
            'icon': '🧬',
            'type': 'local',
            'endpoint': 'http://localhost:11434/api/chat',
            'models': [
                {'id': 'unsloth-llama3.3:70b', 'name': 'Unsloth Llama 3.3 70B', 'context': 128000, 'free': True},
                {'id': 'unsloth-llama3.1:8b', 'name': 'Unsloth Llama 3.1 8B', 'context': 128000, 'free': True},
                {'id': 'unsloth-qwen2.5:7b', 'name': 'Unsloth Qwen 2.5 7B', 'context': 32768, 'free': True},
            ],
        },
        'llm_studio': {
            'name': 'LLM Studio',
            'icon': '🏗️',
            'type': 'local',
            'endpoint': 'http://localhost:1234/v1/chat/completions',
            'models': [
                {'id': 'llm-studio-default', 'name': 'LLM Studio Default', 'context': 128000, 'free': True},
            ],
        },
        'lm_studio': {
            'name': 'LM Studio',
            'icon': '🖥️',
            'type': 'local',
            'endpoint': 'http://localhost:1234/v1/chat/completions',
            'models': [
                {'id': 'lm-studio-default', 'name': 'LM Studio Default', 'context': 128000, 'free': True},
                {'id': 'lm-studio-custom', 'name': 'LM Studio Custom Model', 'context': 128000, 'free': True},
            ],
        },
    }
    
    STYLE_PRESETS = {
        'SaaS': {'colors': {'primary': '#3b82f6', 'secondary': '#8b5cf6', 'accent': '#f59e0b', 'bg': '#ffffff', 'text': '#1e293b'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}},
        'Modern Dark': {'colors': {'primary': '#6366f1', 'secondary': '#8b5cf6', 'accent': '#f59e0b', 'bg': '#0f172a', 'text': '#f8fafc'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}},
        'Minimal Light': {'colors': {'primary': '#1e293b', 'secondary': '#64748b', 'accent': '#3b82f6', 'bg': '#ffffff', 'text': '#1e293b'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}},
        'Gradient': {'colors': {'primary': '#ec4899', 'secondary': '#8b5cf6', 'accent': '#f59e0b', 'bg': '#ffffff', 'text': '#1e293b'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}},
        'Glassmorphism': {'colors': {'primary': '#6366f1', 'secondary': '#a855f7', 'accent': '#f59e0b', 'bg': '#1e293b', 'text': '#f8fafc'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}},
        'Neumorphism': {'colors': {'primary': '#6366f1', 'secondary': '#8b5cf6', 'accent': '#f59e0b', 'bg': '#e2e8f0', 'text': '#1e293b'}, 'fonts': {'heading': 'Inter', 'body': 'Inter'}},
    }
    
    SECTION_TYPES = {
        'Navbar': {'name': 'Navbar', 'category': 'Navigation', 'props': {'logo': 'WebBuilder', 'links': ['Home', 'About', 'Contact']}},
        'Hero — Centered': {'name': 'Hero — Centered', 'category': 'Hero', 'props': {'type': 'centered', 'title': 'Build Something Amazing', 'subtitle': 'Professional way to create beautiful websites'}},
        'Hero — Split Left': {'name': 'Hero — Split Left', 'category': 'Hero', 'props': {'type': 'split', 'title': 'Transform Your Business', 'subtitle': 'Join thousands of satisfied customers'}},
        'Hero — Minimal': {'name': 'Hero — Minimal', 'category': 'Hero', 'props': {'type': 'minimal', 'title': 'Simple. Clean. Powerful.', 'subtitle': 'Beautiful design meets powerful functionality'}},
        'Features — 3 Columns': {'name': 'Features — 3 Columns', 'category': 'Features', 'props': {'columns': 3, 'features': []}},
        'Features — 4 Columns': {'name': 'Features — 4 Columns', 'category': 'Features', 'props': {'columns': 4, 'features': []}},
        'Features — Cards': {'name': 'Features — Cards', 'category': 'Features', 'props': {'layout': 'cards', 'features': []}},
        'CTA — Simple': {'name': 'CTA — Simple', 'category': 'CTA', 'props': {'title': 'Ready to get started?', 'buttonText': 'Sign Up Now'}},
        'CTA — Split': {'name': 'CTA — Split', 'category': 'CTA', 'props': {'title': 'Start your free trial', 'buttonText': 'Get Started'}},
        'Pricing — 3 Tiers': {'name': 'Pricing — 3 Tiers', 'category': 'Pricing', 'props': {'tiers': 3, 'plans': []}},
        'Pricing — 2 Tiers': {'name': 'Pricing — 2 Tiers', 'category': 'Pricing', 'props': {'tiers': 2, 'plans': []}},
        'Stats': {'name': 'Stats', 'category': 'Social Proof', 'props': {'stats': []}},
        'Testimonials — 2 Columns': {'name': 'Testimonials — 2 Columns', 'category': 'Social Proof', 'props': {'columns': 2, 'testimonials': []}},
        'Testimonials — 3 Columns': {'name': 'Testimonials — 3 Columns', 'category': 'Social Proof', 'props': {'columns': 3, 'testimonials': []}},
        'FAQ': {'name': 'FAQ', 'category': 'Content', 'props': {'questions': []}},
        'Footer': {'name': 'Footer', 'category': 'Navigation', 'props': {'links': [], 'social': []}},
    }
    
    SECTIONS = {
        'Navbar': {
            'icon': '🔍',
            'props_template': {
                'logo': 'WebBuilder',
                'links': ['Home', 'About', 'Contact'],
                'ctaText': 'Get Started',
                'ctaLink': '#',
            }
        },
        'Hero — Centered': {
            'icon': '🎯',
            'props_template': {
                'type': 'centered',
                'title': 'Build Something Amazing',
                'subtitle': 'The professional way to create beautiful websites and applications',
                'ctaText': 'Get Started',
                'ctaColor': '#3b82f6',
            }
        },
        'Hero — Split Left': {
            'icon': '✂️',
            'props_template': {
                'type': 'split',
                'title': 'Transform Your Business',
                'subtitle': 'Join thousands of satisfied customers',
                'ctaText': 'Start Free Trial',
                'ctaColor': '#1e293b',
                'image': 'https://picsum.photos/seed/demo/800/600',
            }
        },
        'Hero — Minimal': {
            'icon': '🎨',
            'props_template': {
                'type': 'minimal',
                'title': 'Simple. Clean. Powerful.',
                'subtitle': 'Beautiful design meets powerful functionality',
                'ctaText': 'Learn More',
            }
        },
        'Features — 3 Columns': {
            'icon': '🔲',
            'props_template': {
                'columns': 3,
                'features': [
                    {'title': 'Fast', 'description': 'Lightning fast performance'},
                    {'title': 'Secure', 'description': 'Enterprise-grade security'},
                    {'title': 'Scalable', 'description': 'Grows with your business'},
                ]
            }
        },
        'Features — 4 Columns': {
            'icon': '🔳',
            'props_template': {
                'columns': 4,
                'features': [
                    {'title': 'Fast', 'description': 'Lightning fast performance'},
                    {'title': 'Secure', 'description': 'Enterprise-grade security'},
                    {'title': 'Scalable', 'description': 'Grows with your business'},
                    {'title': 'Reliable', 'description': '99.9% uptime guaranteed'},
                ]
            }
        },
        'Features — Cards': {
            'icon': '💳',
            'props_template': {
                'layout': 'cards',
                'features': [
                    {'title': 'Design', 'description': 'Beautiful, modern design'},
                    {'title': 'Develop', 'description': 'Clean, maintainable code'},
                    {'title': 'Deploy', 'description': 'One-click deployment'},
                ]
            }
        },
        'CTA — Simple': {
            'icon': '📢',
            'props_template': {
                'title': 'Ready to get started?',
                'subtitle': 'Join thousands of satisfied customers',
                'buttonText': 'Sign Up Now',
                'buttonColor': '#3b82f6',
            }
        },
        'CTA — Split': {
            'icon': '🔀',
            'props_template': {
                'title': 'Start your free trial',
                'subtitle': 'No credit card required',
                'buttonText': 'Get Started',
                'buttonColor': '#3b82f6',
            }
        },
        'Pricing — 3 Tiers': {
            'icon': '💰',
            'props_template': {
                'tiers': 3,
                'plans': [
                    {'name': 'Starter', 'price': '$0', 'features': ['1 Project', 'Basic Support']},
                    {'name': 'Pro', '$29': '/mo', 'features': ['Unlimited Projects', 'Priority Support']},
                    {'name': 'Enterprise', '$99': '/mo', 'features': ['Custom Solutions', '24/7 Support']},
                ]
            }
        },
        'Pricing — 2 Tiers': {
            'icon': '💸',
            'props_template': {
                'tiers': 2,
                'plans': [
                    {'name': 'Basic', 'price': '$0', 'features': ['1 Project', 'Basic Support']},
                    {'name': 'Premium', '$29': '/mo', 'features': ['Unlimited Projects', 'Priority Support']},
                ]
            }
        },
        'Stats': {
            'icon': '📊',
            'props_template': {
                'stats': [
                    {'label': 'Users', 'value': '10K+'},
                    {'label': 'Projects', 'value': '50K+'},
                    {'label': 'Uptime', 'value': '99.9%'},
                ]
            }
        },
        'Testimonials — 2 Columns': {
            'icon': '💬',
            'props_template': {
                'columns': 2,
                'testimonials': [
                    {'name': 'John Doe', 'role': 'CEO', 'text': 'Amazing product!'},
                    {'name': 'Jane Smith', 'role': 'CTO', 'text': 'Transformed our workflow.'},
                ]
            }
        },
        'Testimonials — 3 Columns': {
            'icon': '🗣️',
            'props_template': {
                'columns': 3,
                'testimonials': [
                    {'name': 'John Doe', 'role': 'CEO', 'text': 'Amazing product!'},
                    {'name': 'Jane Smith', 'role': 'CTO', 'text': 'Transformed our workflow.'},
                    {'name': 'Bob Johnson', 'role': 'Dev', 'text': 'Best tool ever.'},
                ]
            }
        },
        'FAQ': {
            'icon': '❓',
            'props_template': {
                'questions': [
                    {'q': 'What is WebBuilder?', 'a': 'A professional web builder platform.'},
                    {'q': 'Is it free?', 'a': 'Yes, we offer a free tier.'},
                ]
            }
        },
        'Footer': {
            'icon': '📎',
            'props_template': {
                'links': ['Home', 'About', 'Contact', 'Privacy'],
                'social': ['Twitter', 'GitHub', 'Discord'],
            }
        },
    }

class ConfigManager:
    """Manages configuration, API keys, and settings persistence."""
    
    def __init__(self, config_path=None):
        self.config_path = config_path or str(Path.home() / '.webbuilder' / 'config.json')
        self._ensure_directories()
        self.config = self._load()
    
    def _ensure_directories(self):
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            'providers': {},
            'settings': {
                'theme': 'dark',
                'font_size': 14,
                'auto_save': True,
                'auto_save_interval': 30,
            },
        }
    
    def save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_api_key(self, provider_id):
        return self.config.get('providers', {}).get(provider_id, {}).get('api_key', '')
    
    def set_api_key(self, provider_id, api_key):
        self.config.setdefault('providers', {})[provider_id] = {
            'api_key': api_key,
            'models': [],
            'last_updated': datetime.now().isoformat(),
        }
        self.save()
    
    def get_setting(self, key, default=None):
        return self.config.get('settings', {}).get(key, default)
    
    def set_setting(self, key, value):
        self.config.setdefault('settings', {})
        self.config['settings'][key] = value
        self.save()
    
    def get_provider_config(self, provider_id):
        return self.config.get('providers', {}).get(provider_id, {})
    
    def list_providers(self):
        return list(Config.ALL_PROVIDERS.keys())
    
    def set_key(self, provider_id, api_key):
        return self.set_api_key(provider_id, api_key)
    
    def get_key(self, provider_id):
        return self.get_api_key(provider_id)


# ═══════════════════════════════════════════════════════════════════════════
# MODEL ROUTER
# ═══════════════════════════════════════════════════════════════════════════

class ModelRouter:
    """Routes chat requests to appropriate provider and model."""
    
    def __init__(self, config_manager=None):
        self.config = config_manager or ConfigManager()
        self._load_providers()
    
    def _load_providers(self):
        self.available_providers = {}
        for pid in Config.ALL_PROVIDERS:
            provider_cfg = self.config.get_provider_config(pid)
            if provider_cfg.get('api_key'):
                self.available_providers[pid] = {
                    'models': provider_cfg.get('models', []),
                    'api_key': provider_cfg['api_key'],
                    'provider_info': Config.ALL_PROVIDERS[pid],
                }
    
    def get_available_models(self, provider_id=None):
        if provider_id:
            return self.available_providers.get(provider_id, {}).get('models', [])
        result = {}
        for pid, info in self.available_providers.items():
            result[pid] = info['models']
        return result
    
    def route(self, provider_id, model_name, message, system_prompt=None, max_tokens=1024):
        provider_info = Config.ALL_PROVIDERS.get(provider_id)
        if not provider_info:
            raise ValueError(f"Unknown provider: {provider_id}")
        
        provider_cfg = self.config.get_provider_config(provider_id)
        api_key = provider_cfg.get('api_key')
        if not api_key:
            raise ValueError(f"No API key configured for {provider_info['name']}")
        
        return {
            'provider': provider_id,
            'model': model_name,
            'api_key_status': 'configured' if api_key else 'missing',
            'provider_info': provider_info,
            'message': message,
            'system_prompt': system_prompt,
            'max_tokens': max_tokens,
        }


# ═══════════════════════════════════════════════════════════════════════════
# HTML EXPORTER
# ═══════════════════════════════════════════════════════════════════════════

class HTMLExporter:
    """Exports WebBuilder projects to standalone HTML files."""
    
    def __init__(self, project=None):
        self.project = project or {
            'id': 'export-' + datetime.now().strftime('%Y%m%d-%H%M%S'),
            'name': 'Untitled Project',
            'styles': 'SaaS',
            'sections': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
    
    def _section_to_html(self, section, index):
        section_type = section.get('type', 'div').lower().replace(' — ', '_').replace(' ', '_').replace('-', '_')
        props = section.get('props', {})
        section_id = f'section-{index}'
        
        if section_type in ['navbar', 'nav']:
            logo = props.get('logo', 'Brand')
            links = props.get('links', [])
            cta_text = props.get('ctaText', '')
            cta_link = props.get('ctaLink', '#')
            return f'''
        <section id="{section_id}" class="navbar">
            <div class="navbar-container">
                <div class="navbar-logo">{logo}</div>
                <nav class="navbar-links">
                    {''.join(f'<a href="#">{link}</a>' for link in links)}
                </nav>
                {f'<a href="{cta_link}" class="btn-primary">{cta_text}</a>' if cta_text else ''}
            </div>
        </section>'''
        
        elif section_type in ['hero', 'hero_centered', 'hero_split', 'hero_minimal', 'hero_split_left']:
            title = props.get('title', 'Welcome')
            subtitle = props.get('subtitle', '')
            cta_text = props.get('ctaText', '')
            cta_color = props.get('ctaColor', '#3b82f6')
            hero_type = props.get('type', 'centered')
            bg_color = props.get('backgroundColor', '#ffffff')
            text_color = props.get('textColor', 'inherit')
            
            if hero_type == 'split':
                image = props.get('image', '')
                image_html = f'<div class="hero-image" style="background-image: url({image})"></div>' if image else ''
                return f'''
        <section id="{section_id}" class="hero hero-split" style="background: {bg_color}; color: {text_color};">
            <div class="hero-content">
                <h1 class="hero-title">{title}</h1>
                {f'<p class="hero-subtitle">{subtitle}</p>' if subtitle else ''}
                {f'<a href="#" class="btn-primary" style="background: {cta_color}">{cta_text}</a>' if cta_text else ''}
            </div>
            {image_html}
        </section>'''
            
            return f'''
        <section id="{section_id}" class="hero hero-{hero_type}" style="background: {bg_color}; color: {text_color};">
            <div class="hero-content">
                <h1 class="hero-title">{title}</h1>
                {f'<p class="hero-subtitle">{subtitle}</p>' if subtitle else ''}
                {f'<a href="#" class="btn-primary" style="background: {cta_color}">{cta_text}</a>' if cta_text else ''}
            </div>
        </section>'''
        
        elif section_type in ['features', 'features_3cols', 'features_4cols', 'features_cards', 'features_grid_3', 'features_grid_4', 'features_3_columns', 'features_4_columns']:
            title = props.get('title', 'Features')
            subtitle = props.get('subtitle', '')
            columns = props.get('columns', 3)
            items = props.get('items', []) or props.get('features', [])
            
            if 'cards' in section_type:
                items_html = ''
                for item in items[:6]:
                    items_html += f'''
                    <div class="feature-card">
                        <div class="feature-icon">{item.get('icon', '✨')}</div>
                        <h3 class="feature-card-title">{item.get('title', '')}</h3>
                        <p class="feature-card-desc">{item.get('description', '')}</p>
                    </div>'''
            else:
                per_col = max(1, len(items) // columns) if items else 0
                items_html = ''
                for i, item in enumerate(items[:columns * per_col]):
                    items_html += f'''
                    <div class="feature-item">
                        <div class="feature-icon">{item.get('icon', '✨')}</div>
                        <h3 class="feature-item-title">{item.get('title', '')}</h3>
                        <p class="feature-item-desc">{item.get('description', '')}</p>
                    </div>'''
            
            return f'''
        <section id="{section_id}" class="features features-{columns}cols">
            <div class="section-container">
                <h2 class="section-title">{title}</h2>
                {f'<p class="section-subtitle">{subtitle}</p>' if subtitle else ''}
                <div class="features-grid">
                    {items_html}
                </div>
            </div>
        </section>'''
        
        elif section_type in ['cta', 'cta_simple', 'cta_split']:
            title = props.get('title', 'Ready to Get Started?')
            subtitle = props.get('subtitle', '')
            button_text = props.get('buttonText', 'Get Started')
            button_color = props.get('buttonColor', '#3b82f6')
            bg_color = props.get('backgroundColor', '#3b82f6')
            text_color = props.get('textColor', '#ffffff')
            cta_type = props.get('type', 'simple')
            
            if cta_type == 'split':
                image = props.get('image', '')
                image_html = f'<div class="cta-image" style="background-image: url({image})"></div>' if image else ''
                return f'''
        <section id="{section_id}" class="cta cta-split" style="background: {bg_color};">
            <div class="cta-content">
                <h2 class="cta-title" style="color: {text_color}">{title}</h2>
                {f'<p class="cta-subtitle" style="color: {text_color}">{subtitle}</p>' if subtitle else ''}
                <a href="#" class="btn-white">{button_text}</a>
            </div>
            {image_html}
        </section>'''
            
            return f'''
        <section id="{section_id}" class="cta cta-simple" style="background: {bg_color};">
            <div class="cta-container">
                <h2 class="cta-title" style="color: {text_color}">{title}</h2>
                {f'<p class="cta-subtitle" style="color: {text_color}">{subtitle}</p>' if subtitle else ''}
                <a href="#" class="btn-white">{button_text}</a>
            </div>
        </section>'''
        
        elif section_type in ['pricing', 'pricing_tiers', 'pricing_card', 'pricing_3_tiers', 'pricing_2_tiers']:
            title = props.get('title', 'Pricing')
            subtitle = props.get('subtitle', '')
            tiers = props.get('tiers', [])
            if isinstance(tiers, int):
                # Generate default tiers if just a number
                tiers = [
                    {'name': 'Starter', 'price': '$0', 'features': ['1 Project', 'Basic Support']},
                    {'name': 'Pro', 'price': '$29', 'features': ['Unlimited Projects', 'Priority Support']},
                    {'name': 'Enterprise', 'price': '$99', 'features': ['Custom Solutions', '24/7 Support']},
                ][:tiers]
            currency = props.get('currency', '$')
            highlight_tier = props.get('highlight', 1)
            
            tiers_html = ''
            for i, tier in enumerate(tiers):
                is_highlight = i == highlight_tier
                tier_class = 'pricing-tier highlighted' if is_highlight else 'pricing-tier'
                badge = '<span class="popular-badge">Most Popular</span>' if is_highlight else ''
                tiers_html += f'''
                <div class="{tier_class}">
                    {badge}
                    <h3 class="tier-name">{tier.get('name', f'Tier {i+1}')}</h3>
                    <div class="tier-price"><span class="price-currency">{currency}</span><span class="price-amount">{tier.get('price', '')}</span><span class="price-period">/{tier.get('period', 'mo')}</span></div>
                    <p class="tier-description">{tier.get('description', '')}</p>
                    <ul class="tier-features">
                        {''.join(f'<li>{feat}</li>' for feat in tier.get('features', []))}
                    </ul>
                    <a href="#" class="btn-outline">{tier.get('cta', 'Choose Plan')}</a>
                </div>'''
            
            return f'''
        <section id="{section_id}" class="pricing">
            <div class="section-container">
                <h2 class="section-title text-center">{title}</h2>
                {f'<p class="section-subtitle text-center">{subtitle}</p>' if subtitle else ''}
                <div class="pricing-grid">
                    {tiers_html}
                </div>
            </div>
        </section>'''
        
        elif section_type in ['stats', 'stats_bar']:
            title = props.get('title', 'Trusted Worldwide')
            subtitle = props.get('subtitle', '')
            items = props.get('items', [])
            styles = props.get('styles', [])
            
            items_html = ''
            for i, item in enumerate(items):
                style = styles[i] if i < len(styles) else {'color': '#3b82f6'}
                items_html += f'''
                    <div class="stat-item">
                        <div class="stat-value" style="color: {style.get('color', '#3b82f6')}">{item.get('value', '')}</div>
                        <div class="stat-label">{item.get('label', '')}</div>
                    </div>'''
            
            return f'''
        <section id="{section_id}" class="stats">
            <div class="section-container">
                <h2 class="section-title text-center">{title}</h2>
                {f'<p class="section-subtitle text-center">{subtitle}</p>' if subtitle else ''}
                <div class="stats-grid">
                    {items_html}
                </div>
            </div>
        </section>'''
        
        elif section_type in ['testimonials', 'testimonials_2cols', 'testimonials_3cols']:
            title = props.get('title', 'What Our Customers Say')
            subtitle = props.get('subtitle', '')
            columns = 2 if '2cols' in section_type else 3
            items = props.get('items', [])
            
            items_html = ''
            for i, item in enumerate(items):
                quote = item.get('quote', '')
                author = item.get('author', '')
                role = item.get('role', '')
                items_html += f'''
                    <div class="testimonial-item">
                        <div class="testimonial-quote">"{quote}"</div>
                        <div class="testimonial-author">
                            <div class="testimonial-name">{author}</div>
                            <div class="testimonial-role">{role}</div>
                        </div>
                    </div>'''
            
            return f'''
        <section id="{section_id}" class="testimonials testimonials-{columns}cols">
            <div class="section-container">
                <h2 class="section-title text-center">{title}</h2>
                {f'<p class="section-subtitle text-center">{subtitle}</p>' if subtitle else ''}
                <div class="testimonials-grid">
                    {items_html}
                </div>
            </div>
        </section>'''
        
        elif section_type == 'faq':
            title = props.get('title', 'Frequently Asked Questions')
            subtitle = props.get('subtitle', '')
            questions = props.get('questions', [])
            
            items_html = ''
            for i, q in enumerate(questions):
                items_html += f'''
                    <div class="faq-item">
                        <div class="faq-question">
                            <span>{q.get('q', '')}</span>
                            <span class="faq-toggle">+</span>
                        </div>
                        <div class="faq-answer">{q.get('a', '')}</div>
                    </div>'''
            
            return f'''
        <section id="{section_id}" class="faq">
            <div class="section-container">
                <h2 class="section-title text-center">{title}</h2>
                {f'<p class="section-subtitle text-center">{subtitle}</p>' if subtitle else ''}
                <div class="faq-list">
                    {items_html}
                </div>
            </div>
        </section>'''
        
        elif section_type == 'footer':
            copyright_text = props.get('copyright', '© 2024 WebBuilder. All rights reserved.')
            links = props.get('links', [])
            social = props.get('social', [])
            
            # Handle links as strings or dicts
            links_html = ''
            for link in links:
                if isinstance(link, dict):
                    links_html += f'<a href="{link.get("url", "#")}">{link.get("text", "")}</a>'
                else:
                    links_html += f'<a href="#">{link}</a>'
            
            # Handle social as strings or dicts
            social_html = ''
            for icon in social:
                if isinstance(icon, dict):
                    social_html += f'<a href="#" class="social-link">{icon.get("icon", "")}<span>{icon.get("label", "")}</span></a>'
                else:
                    social_html += f'<a href="#" class="social-link"><span>{icon}</span></a>'
            
            return f'''
        <footer id="{section_id}" class="footer">
            <div class="footer-container">
                <div class="footer-main">
                    <div class="footer-brand">
                        <div class="footer-logo">WebBuilder</div>
                        <p class="footer-copyright">{copyright_text}</p>
                    </div>
                    <div class="footer-links">
                        <div class="footer-link-group">
                            <h4 class="footer-link-title">Product</h4>
                            {links_html}
                        </div>
                        <div class="footer-link-group">
                            <h4 class="footer-link-title">Connect</h4>
                            {social_html}
                        </div>
                    </div>
                </div>
            </div>
        </footer>'''
        
        else:
            content = props.get('content', '')
            return f'''
        <section id="{section_id}" class="section {section_type}">
            <div class="section-container">
                {content}
            </div>
        </section>'''
    
    def generate_html(self):
        """Generate complete HTML document from project."""
        style = self.project.get('styles', 'SaaS')
        style_config = STYLE_PRESETS.get(style, STYLE_PRESETS['SaaS'])
        colors = style_config['colors']
        fonts = style_config['fonts']
        
        # Handle both formats: project.sections OR project.pages[0].sections
        sections = self.project.get('sections', [])
        if not sections and 'pages' in self.project:
            pages = self.project.get('pages', [])
            if pages:
                sections = pages[0].get('sections', [])
        
        sections_html = ''
        for i, section in enumerate(sections):
            sections_html += self._section_to_html(section, i)
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.project.get('name', 'Untitled Project')}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family={fonts['heading']}:wght@400;500;600;700;800&family={fonts['body']}:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        /* ===== Reset ===== */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        /* ===== Base ===== */
        body {{
            font-family: '{fonts['body']}', sans-serif;
            color: {colors['text']};
            background: {colors['bg']};
            line-height: 1.6;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            font-family: '{fonts['heading']}', sans-serif;
            font-weight: 700;
        }}
        
        a {{
            text-decoration: none;
            color: inherit;
        }}
        
        .section-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
        }}
        
        .text-center {{
            text-align: center;
        }}
        
        /* ===== Navbar ===== */
        .navbar {{
            padding: 20px 0;
            background: {colors['bg']};
            border-bottom: 1px solid rgba(0,0,0,0.08);
        }}
        .navbar-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .navbar-logo {{
            font-size: 24px;
            font-weight: 800;
            color: {colors['text']};
            font-family: '{fonts['heading']}';
        }}
        .navbar-links {{
            display: flex;
            gap: 32px;
            align-items: center;
        }}
        .navbar-links a {{
            color: {colors['text']};
            opacity: 0.7;
            font-size: 14px;
            font-weight: 500;
            transition: opacity 0.2s;
        }}
        .navbar-links a:hover {{
            opacity: 1;
        }}
        .btn-primary {{
            background: {colors['primary']};
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .btn-primary:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba({int(colors['primary'].lstrip('#')[0:2], 16)}, {int(colors['primary'].lstrip('#')[2:4], 16)}, {int(colors['primary'].lstrip('#')[4:6], 16)}, 0.4);
        }}
        
        /* ===== Hero ===== */
        .hero {{
            padding: 100px 0;
        }}
        .hero-content {{
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
            padding: 0 24px;
        }}
        .hero-title {{
            font-size: 56px;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 20px;
            color: {colors['text']};
        }}
        .hero-subtitle {{
            font-size: 20px;
            opacity: 0.7;
            margin-bottom: 32px;
            color: {colors['text']};
        }}
        .btn-white {{
            background: white;
            color: {colors['text']};
            padding: 14px 28px;
            border-radius: 10px;
            font-weight: 700;
            font-size: 15px;
        }}
        
        /* ===== Features ===== */
        .features {{
            padding: 80px 0;
            background: {colors['bg']};
        }}
        .section-title {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 12px;
            color: {colors['text']};
        }}
        .section-subtitle {{
            font-size: 16px;
            opacity: 0.6;
            margin-bottom: 48px;
            color: {colors['text']};
        }}
        .features-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 32px;
        }}
        .feature-card {{
            background: rgba(0,0,0,0.02);
            border-radius: 12px;
            padding: 24px;
            border: 1px solid rgba(0,0,0,0.05);
        }}
        .feature-icon {{
            font-size: 32px;
            margin-bottom: 12px;
        }}
        .feature-card-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
            color: {colors['text']};
        }}
        .feature-card-desc {{
            font-size: 14px;
            opacity: 0.6;
            line-height: 1.5;
        }}
        .feature-item {{
            text-align: center;
        }}
        .feature-item-title {{
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 6px;
            color: {colors['text']};
        }}
        .feature-item-desc {{
            font-size: 13px;
            opacity: 0.6;
        }}
        
        /* ===== CTA ===== */
        .cta {{
            padding: 80px 0;
            text-align: center;
        }}
        .cta-container {{
            max-width: 700px;
            margin: 0 auto;
            padding: 0 24px;
        }}
        .cta-title {{
            font-size: 40px;
            font-weight: 800;
            margin-bottom: 16px;
        }}
        .cta-subtitle {{
            font-size: 18px;
            margin-bottom: 32px;
            opacity: 0.8;
        }}
        .btn-white {{
            display: inline-block;
            background: white;
            color: {colors['text']};
            padding: 14px 28px;
            border-radius: 10px;
            font-weight: 700;
            font-size: 15px;
        }}
        
        /* ===== Pricing ===== */
        .pricing {{
            padding: 80px 0;
            background: {colors['bg']};
        }}
        .pricing-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
            margin-top: 48px;
        }}
        .pricing-tier {{
            background: white;
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 16px;
            padding: 32px;
            position: relative;
        }}
        .pricing-tier.highlighted {{
            border-color: {colors['primary']};
            box-shadow: 0 0 0 1px {colors['primary']}, 0 8px 24px rgba(0,0,0,0.08);
        }}
        .popular-badge {{
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: {colors['primary']};
            color: white;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 20px;
        }}
        .tier-name {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
        }}
        .tier-price {{
            font-size: 36px;
            font-weight: 800;
            margin-bottom: 8px;
            color: {colors['text']};
        }}
        .price-currency {{
            font-size: 18px;
            font-weight: 600;
            vertical-align: top;
            margin-right: 2px;
        }}
        .price-period {{
            font-size: 14px;
            font-weight: 400;
            opacity: 0.5;
        }}
        .tier-description {{
            font-size: 14px;
            opacity: 0.6;
            margin-bottom: 20px;
        }}
        .tier-features {{
            list-style: none;
            margin-bottom: 24px;
        }}
        .tier-features li {{
            font-size: 14px;
            padding: 6px 0;
            border-bottom: 1px solid rgba(0,0,0,0.04);
            opacity: 0.7;
        }}
        .btn-outline {{
            display: block;
            text-align: center;
            border: 2px solid {colors['primary']};
            color: {colors['primary']};
            padding: 12px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
        }}
        
        /* ===== Stats ===== */
        .stats {{
            padding: 60px 0;
            background: {colors['primary']};
            color: white;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 24px;
            margin-top: 40px;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 8px;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.8;
        }}
        
        /* ===== Testimonials ===== */
        .testimonials {{
            padding: 80px 0;
            background: {colors['bg']};
        }}
        .testimonials-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
            margin-top: 48px;
        }}
        .testimonial-item {{
            background: rgba(0,0,0,0.02);
            border-radius: 12px;
            padding: 24px;
            border: 1px solid rgba(0,0,0,0.05);
        }}
        .testimonial-quote {{
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 16px;
            opacity: 0.8;
            font-style: italic;
        }}
        .testimonial-author {{
            border-top: 1px solid rgba(0,0,0,0.08);
            padding-top: 12px;
        }}
        .testimonial-name {{
            font-size: 14px;
            font-weight: 600;
        }}
        .testimonial-role {{
            font-size: 12px;
            opacity: 0.5;
        }}
        
        /* ===== FAQ ===== */
        .faq {{
            padding: 80px 0;
            background: {colors['bg']};
        }}
        .faq-list {{
            max-width: 700px;
            margin: 40px auto 0;
        }}
        .faq-item {{
            border-bottom: 1px solid rgba(0,0,0,0.08);
        }}
        .faq-question {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 0;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
        }}
        .faq-toggle {{
            font-size: 24px;
            color: {colors['primary']};
        }}
        .faq-answer {{
            padding: 0 0 16px;
            font-size: 14px;
            opacity: 0.6;
            line-height: 1.5;
            display: none;
        }}
        
        /* ===== Footer ===== */
        .footer {{
            padding: 48px 0;
            background: #0f172a;
            color: white;
        }}
        .footer-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
        }}
        .footer-main {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .footer-logo {{
            font-size: 20px;
            font-weight: 800;
            font-family: '{fonts['heading']}';
            margin-bottom: 8px;
        }}
        .footer-copyright {{
            font-size: 13px;
            opacity: 0.5;
        }}
        .footer-links {{
            display: flex;
            gap: 48px;
        }}
        .footer-link-group {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .footer-link-title {{
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.5;
        }}
        .footer-links a {{
            font-size: 13px;
            opacity: 0.7;
        }}
        .footer-links a:hover {{
            opacity: 1;
        }}
        .social-link {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            opacity: 0.7;
        }}
        
        /* ===== Responsive ===== */
        @media (max-width: 768px) {{
            .hero-title {{
                font-size: 36px;
            }}
            .features-grid,
            .pricing-grid,
            .testimonials-grid,
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            .navbar-container {{
                flex-direction: column;
                gap: 16px;
            }}
            .footer-main {{
                flex-direction: column;
                gap: 32px;
            }}
        }}
    </style>
</head>
<body>
{sections_html}
</body>
</html>'''
    
    def export(self, output_path):
        """Export project to HTML file."""
        html = self.generate_html()
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return output_path


# ═══════════════════════════════════════════════════════════════════════════
# API KEY MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class APIKeyManager:
    """Manages API keys for all providers."""
    
    def __init__(self, config_manager=None):
        self.config = config_manager or ConfigManager()
    
    def set_key(self, provider_id, api_key):
        self.config.set_api_key(provider_id, api_key)
        return True
    
    def get_key(self, provider_id):
        return self.config.get_api_key(provider_id)
    
    def has_key(self, provider_id):
        return bool(self.config.get_api_key(provider_id))
    
    def is_local(self, provider_id):
        """Check if a provider is local."""
        info = Config.ALL_PROVIDERS.get(provider_id, {})
        return info.get('type') == 'local'
    
    def list_configured_providers(self):
        result = []
        for pid in Config.ALL_PROVIDERS:
            if self.has_key(pid):
                result.append(pid)
        return result
    
    def delete_key(self, provider_id):
        providers = self.config.config.setdefault('providers', {})
        if provider_id in providers:
            del providers[provider_id]
            self.config.save()
        return True


# ═══════════════════════════════════════════════════════════════════════════
# NEURAL NETWORK ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class DenseLayer:
    def __init__(self, in_size, out_size):
        self.W = np.random.randn(in_size, out_size).astype(np.float32) * np.sqrt(2.0 / in_size)
        self.b = np.zeros(out_size, dtype=np.float32)
        self.x = None

    def forward(self, x):
        self.x = x
        return x @ self.W + self.b

    def backward(self, dout):
        self.dW = self.x.T @ dout
        self.db = np.sum(dout, axis=0)
        return dout @ self.W.T

    def update(self, lr):
        self.W -= lr * self.dW
        self.b -= lr * self.db


class ReLULayer:
    def forward(self, x):
        self.mask = (x > 0)
        return x * self.mask

    def backward(self, dout):
        return dout * self.mask

    def update(self, lr):
        pass


class NeuralNetwork:
    def __init__(self, layers):
        self.layers = layers
        self.history = []

    def forward(self, x):
        out = self.layers[0].forward(x)
        for L in self.layers[1:]:
            out = L.forward(out)
        return out

    def backward(self, dout, lr=0.01):
        n = len(self.layers)
        for i in range(n - 1, -1, -1):
            if i == n - 1:
                dout = self.layers[i].backward(dout)
            else:
                dout = self.layers[i].backward(dout)
            self.layers[i].update(lr)

    def train(self, X, y, epochs, lr=0.01):
        self.history = []
        for epoch in range(epochs):
            pred = self.forward(X)
            loss = np.mean((pred - y) ** 2)
            dout = 2 * (pred - y) / len(X)
            self.backward(dout, lr)
            if epoch % 100 == 0:
                self.history.append({'epoch': epoch, 'loss': float(loss)})
                yield epoch, float(loss)

    def predict(self, x):
        return self.forward(x)


# ═══════════════════════════════════════════════════════════════════════════
# ADAPTIVE COLOR GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

class ColorGenerator:
    """Generate color palettes using neural inspiration"""

    def __init__(self):
        self.model = NeuralNetwork([
            DenseLayer(3, 16),
            ReLULayer(),
            DenseLayer(16, 8),
            ReLULayer(),
            DenseLayer(8, 3),
        ])

    def generate_palette(self, style=None):
        """Generate a color palette based on style"""
        if style:
            styles = {
                'saas': [0.24, 0.51, 0.97],
                'creative': [0.93, 0.29, 0.60],
                'minimal': [0.0, 0.0, 0.0],
                'modern': [0.02, 0.71, 0.83],
                'dark': [0.04, 0.10, 0.15],
                'corporate': [0.12, 0.25, 0.68],
            }
            seed = styles.get(style, [0.24, 0.51, 0.97])
        else:
            seed = [random.random() for _ in range(3)]

        palette = {
            'primary': self._to_hex(seed),
            'secondary': self._to_hex([min(1, seed[1] + 0.2), min(1, seed[0] - 0.2), seed[2]]),
            'accent': self._to_hex([seed[0], seed[1] * 0.7, seed[2] * 1.2]),
            'bg': '#ffffff' if style != 'dark' and style != 'modern' else '#0f172a',
            'text': '#1e293b' if style != 'dark' and style != 'modern' else '#f8fafc',
        }
        return palette

    def _to_hex(self, rgb):
        return '#' + ''.join([f'{int(c * 255):02x}' for c in rgb])


# ═══════════════════════════════════════════════════════════════════════════
# SECTION WIDGET RENDERER
# ═══════════════════════════════════════════════════════════════════════════

class SectionWidget(QFrame):
    def __init__(self, section_type, props=None):
        super().__init__()
        info = SECTIONS.get(section_type, {'icon': '📄', 'props_template': {}})
        self.section_type = section_type
        self.props = props or info['props_template'].copy()
        self.info = info
        self.setStyleSheet("background: white; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;")
        self._render()

    def _render(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 32, 24, 32)

        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet("background: rgba(30, 30, 44, 0.8); border: 1px solid rgba(255,255,255,0.08); border-bottom: 1px solid rgba(255,255,255,0.12); border-top-left-radius: 10px; border-top-right-radius: 10px;")
        hlayout = QHBoxLayout(header)
        icon = QLabel(self.info.get('icon', '📄'))
        icon.setStyleSheet("font-size: 20px; padding-right: 12px;")
        hlayout.addWidget(icon)
        name = QLabel(self.section_type)
        name.setStyleSheet("color: #e2e8f0; font-weight: 600; font-size: 13px;")
        hlayout.addWidget(name)
        hlayout.addStretch()
        type_label = QLabel(f"<small style='color:#64748b; font-size:9px;'>{self.section_type.lower().replace(' ', '-')}</small>")
        hlayout.addWidget(type_label)
        layout.addWidget(header)

        content = QFrame()
        content.setStyleSheet("background: #fafafa; border: 1px solid rgba(0,0,0,0.06); border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; padding: 24px;")
        clayout = QVBoxLayout(content)
        clayout.setSpacing(16)
        self._render_content(clayout, self.props)
        clayout.addStretch()
        layout.addWidget(content)

    def _render_content(self, layout, props):
        if 'navbar' in self.section_type.lower():
            self._render_navbar(layout, props)
        elif 'hero' in self.section_type.lower():
            self._render_hero(layout, props)
        elif 'features' in self.section_type.lower():
            self._render_features(layout, props)
        elif 'pricing' in self.section_type.lower():
            self._render_pricing(layout, props)
        elif 'cta' in self.section_type.lower():
            self._render_cta(layout, props)
        elif 'stats' in self.section_type.lower():
            self._render_stats(layout, props)
        elif 'testimonials' in self.section_type.lower():
            self._render_testimonials(layout, props)
        elif 'faq' in self.section_type.lower():
            self._render_faq(layout, props)
        elif 'footer' in self.section_type.lower():
            self._render_footer(layout, props)

    def _render_navbar(self, layout, props):
        logo_label = QLabel(props.get('logo', 'Brand'))
        logo_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #1e293b;")
        layout.addWidget(logo_label)
        link_layout = QHBoxLayout()
        for link in props.get('links', []):
            link_btn = QPushButton(link)
            link_btn.setStyleSheet("QPushButton { background: transparent; color: #64748b; border: none; padding: 4px 12px; font-size: 13px; font-weight: 500; }")
            link_layout.addWidget(link_btn)
        link_layout.addStretch()
        layout.addLayout(link_layout)
        cta = QPushButton(props.get('ctaText', 'Get Started'))
        cta.setStyleSheet("QPushButton { background: #3b82f6; color: white; border: none; padding: 8px 20px; border-radius: 6px; font-weight: 600; }")
        layout.addWidget(cta)

    def _render_hero(self, layout, props):
        title_label = QLabel(props.get('title', 'Welcome'))
        title_label.setStyleSheet("font-size: 36px; font-weight: 800; color: #1e293b; margin-bottom: 12px;")
        layout.addWidget(title_label)
        subtitle = QLabel(props.get('subtitle', ''))
        subtitle.setStyleSheet("color: #64748b; font-size: 16px; margin-bottom: 32px;")
        layout.addWidget(subtitle)
        cta = QPushButton(props.get('ctaText', 'Get Started'))
        cta.setStyleSheet(f"QPushButton {{ background: {props.get('ctaColor', '#3b82f6')}; color: white; border: none; padding: 12px 28px; border-radius: 8px; font-weight: 700; font-size: 14px; }}")
        layout.addWidget(cta)

    def _render_features(self, layout, props):
        title_label = QLabel(props.get('title', 'Features'))
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #1e293b; margin-bottom: 8px;")
        layout.addWidget(title_label)
        subtitle = QLabel(props.get('subtitle', ''))
        subtitle.setStyleSheet("color: #64748b; margin-bottom: 24px;")
        layout.addWidget(subtitle)
        cols = props.get('columns', 3)
        items_per_col = len(props.get('items', [])) // cols + 1
        item_idx = 0
        items_layout = QHBoxLayout()
        for col in range(cols):
            col_widget = QWidget()
            col_layout = QVBoxLayout(col_widget)
            col_layout.setContentsMargins(0, 0, 16 if col < cols - 1 else 0, 0)
            col_layout.setSpacing(12)
            for _ in range(items_per_col):
                if item_idx >= len(props.get('items', [])):
                    break
                item = props['items'][item_idx]
                item_idx += 1
                item_frame = QFrame()
                item_frame.setStyleSheet("QFrame { background: white; border: 1px solid rgba(0,0,0,0.06); border-radius: 10px; padding: 16px; }")
                item_layout = QVBoxLayout(item_frame)
                item_layout.setSpacing(8)
                item_icon = QLabel(item.get('icon', '✨'))
                item_icon.setStyleSheet("font-size: 32px; padding: 4px 0;")
                item_layout.addWidget(item_icon)
                item_title = QLabel(item.get('title', ''))
                item_title.setStyleSheet("font-weight: 700; font-size: 14px; color: #1e293b;")
                item_layout.addWidget(item_title)
                item_desc = QLabel(item.get('description', ''))
                item_desc.setStyleSheet("color: #64748b; font-size: 12px;")
                item_layout.addWidget(item_desc)
                col_layout.addWidget(item_frame)
            items_layout.addWidget(col_widget)
        layout.addLayout(items_layout)

    def _render_pricing(self, layout, props):
        title_label = QLabel(props.get('title', 'Pricing'))
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #1e293b; margin-bottom: 8px;")
        layout.addWidget(title_label)
        subtitle = QLabel(props.get('subtitle', ''))
        subtitle.setStyleSheet("color: #64748b; margin-bottom: 24px;")
        layout.addWidget(subtitle)
        tiers_layout = QHBoxLayout()
        tiers_layout.setSpacing(16)
        for i, tier in enumerate(props.get('tiers', [])):
            tier_widget = QFrame()
            is_popular = props.get('highlightTier') == i
            tier_widget.setStyleSheet(f"QFrame {{ background: {'white' if not is_popular else '#f8fafc'}; border: {'2px solid #3b82f6' if is_popular else '1px solid rgba(0,0,0,0.06)'}; border-radius: 10px; padding: {'14px' if is_popular else '12px'}; {'box-shadow: 0 2px 10px rgba(59,130,246,0.15);' if is_popular else ''} }}")
            tier_layout = QVBoxLayout(tier_widget)
            name_label = QLabel(tier.get('name', 'Plan'))
            name_label.setStyleSheet("font-weight: 700; font-size: 14px; color: #1e293b;")
            tier_layout.addWidget(name_label)
            price_label = QLabel(tier.get('price', '$0'))
            price_label.setStyleSheet("font-size: 22px; font-weight: 800; color: #3b82f6; margin: 4px 0;")
            tier_layout.addWidget(price_label)
            desc_label = QLabel(tier.get('description', ''))
            desc_label.setStyleSheet("color: #64748b; font-size: 11px; margin-bottom: 12px;")
            tier_layout.addWidget(desc_label)
            for feature in tier.get('features', []):
                f_label = QLabel(f"✓ {feature}")
                f_label.setStyleSheet("color: #94a3b8; font-size: 11px; padding: 3px 0;")
                tier_layout.addWidget(f_label)
            cta = QPushButton("Get Started")
            cta.setStyleSheet("QPushButton { background: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; margin-top: 12px; }")
            tier_layout.addWidget(cta)
            tiers_layout.addWidget(tier_widget)
        layout.addLayout(tiers_layout)

    def _render_cta(self, layout, props):
        cta_frame = QFrame()
        cta_frame.setStyleSheet(f"QFrame {{ background: {props.get('backgroundColor', '#3b82f6')}; border-radius: 12px; padding: 32px; }}")
        cta_layout = QVBoxLayout(cta_frame)
        title_label = QLabel(props.get('title', 'Ready to Get Started?'))
        title_label.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {props.get('textColor', '#ffffff')}; margin-bottom: 8px;")
        cta_layout.addWidget(title_label)
        subtitle = QLabel(props.get('subtitle', ''))
        subtitle.setStyleSheet(f"color: {props.get('textColor', '#ffffff')}80; font-size: 14px; margin-bottom: 24px;")
        cta_layout.addWidget(subtitle)
        cta_btn = QPushButton(props.get('buttonText', 'Get Started'))
        cta_btn.setStyleSheet(f"QPushButton {{ background: {props.get('buttonColor', 'white')}; color: {props.get('backgroundColor', '#3b82f6')}; border: none; padding: 12px 28px; border-radius: 8px; font-weight: 700; font-size: 14px; }}")
        cta_layout.addWidget(cta_btn)
        layout.addWidget(cta_frame)

    def _render_stats(self, layout, props):
        title_label = QLabel(props.get('title', 'Stats'))
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #1e293b; margin-bottom: 8px;")
        layout.addWidget(title_label)
        subtitle = QLabel(props.get('subtitle', ''))
        subtitle.setStyleSheet("color: #64748b; margin-bottom: 24px;")
        layout.addWidget(subtitle)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(24)
        for item in props.get('items', []):
            stat_widget = QFrame()
            stat_widget.setStyleSheet("QFrame { background: #f8fafc; border: 1px solid rgba(0,0,0,0.06); border-radius: 10px; padding: 20px; }")
            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.setSpacing(4)
            value_label = QLabel(item.get('value', '0'))
            value_label.setStyleSheet("font-size: 28px; font-weight: 800; color: #3b82f6;")
            stat_layout.addWidget(value_label)
            label = QLabel(item.get('label', ''))
            label.setStyleSheet("color: #64748b; font-size: 12px;")
            stat_layout.addWidget(label)
            stats_layout.addWidget(stat_widget)
        layout.addLayout(stats_layout)

    def _render_testimonials(self, layout, props):
        title_label = QLabel(props.get('title', 'Testimonials'))
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #1e293b; margin-bottom: 8px;")
        layout.addWidget(title_label)
        subtitle = QLabel(props.get('subtitle', ''))
        subtitle.setStyleSheet("color: #64748b; margin-bottom: 24px;")
        layout.addWidget(subtitle)
        t_layout = QHBoxLayout()
        t_layout.setSpacing(16)
        for item in props.get('items', []):
            t_widget = QFrame()
            t_widget.setStyleSheet("QFrame { background: #f8fafc; border: 1px solid rgba(0,0,0,0.06); border-radius: 10px; padding: 20px; }")
            t_layout_inner = QVBoxLayout(t_widget)
            t_layout_inner.setSpacing(8)
            quote = QLabel(f'"{item.get("quote", "")}"')
            quote.setStyleSheet("color: #64748b; font-size: 13px; font-style: italic;")
            t_layout_inner.addWidget(quote)
            author_layout = QHBoxLayout()
            author = QLabel(item.get('author', ''))
            author.setStyleSheet("font-weight: 700; font-size: 12px; color: #1e293b; margin-right: 12px;")
            author_layout.addWidget(author)
            role = QLabel(item.get('role', ''))
            role.setStyleSheet("color: #94a3b8; font-size: 11px;")
            author_layout.addWidget(role)
            t_layout_inner.addLayout(author_layout)
            t_layout.addWidget(t_widget)
        layout.addLayout(t_layout)

    def _render_faq(self, layout, props):
        title_label = QLabel(props.get('title', 'FAQ'))
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #1e293b; margin-bottom: 8px;")
        layout.addWidget(title_label)
        subtitle = QLabel(props.get('subtitle', ''))
        subtitle.setStyleSheet("color: #64748b; margin-bottom: 24px;")
        layout.addWidget(subtitle)
        for q_item in props.get('questions', []):
            q_widget = QFrame()
            q_widget.setStyleSheet("QFrame { background: #f8fafc; border: 1px solid rgba(0,0,0,0.06); border-radius: 8px; margin-bottom: 8px; }")
            q_layout = QVBoxLayout(q_widget)
            q_layout.setContentsMargins(16, 12, 16, 12)
            q_label = QLabel(f"Q: {q_item.get('q', '')}")
            q_label.setStyleSheet("font-weight: 600; color: #1e293b;")
            q_layout.addWidget(q_label)
            a_label = QLabel(f'A: {q_item.get("a", "")}')
            a_label.setStyleSheet("color: #64748b; font-size: 13px; padding-top: 8px;")
            q_layout.addWidget(a_label)
            layout.addWidget(q_widget)

    def _render_footer(self, layout, props):
        copyright_label = QLabel(props.get('copyright', '© 2024'))
        copyright_label.setStyleSheet("color: #94a3b8; font-size: 12px; text-align: center; padding: 20px 0;")
        layout.addWidget(copyright_label)
        link_layout = QHBoxLayout()
        link_layout.addStretch()
        for link in props.get('links', []):
            link_btn = QPushButton(link.get('text', ''))
            link_btn.setStyleSheet("QPushButton { background: transparent; color: #94a3b8; border: none; padding: 0 12px; font-size: 12px; }")
            link_layout.addWidget(link_btn)
        link_layout.addStretch()
        layout.addLayout(link_layout)

    def get_props(self):
        return self.section_type, self.props.copy()

    def update_props(self, new_props):
        self.props.update(new_props)
        self._render()


# ═══════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

class WebBuilderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebBuilder Desktop — Professional Web Builder")
        self.setMinimumSize(1400, 800)
        self.resize(1920, 1080)

        self.project = {
            'id': f'project-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'name': 'Untitled Project',
            'pages': [{'id': 'page-1', 'name': 'Home', 'sections': []}],
            'currentPage': 0,
            'design': STYLE_PRESETS['SaaS'].copy(),
        }
        self.selected_section = None
        self.history = []
        self.history_index = -1

        self.init_ui()
        self.render_canvas()
        self.render_properties()

    def init_ui(self):
        self.setStyleSheet(STYLESHEET)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # ── Menu Bar ──
        menubar = self.menuBar()
        file_menu = menubar.addMenu("📁 File")
        file_menu.addAction("New Project", self.new_project, "Ctrl+N")
        file_menu.addAction("Open Project", self.load_project, "Ctrl+O")
        file_menu.addAction("Save Project", self.save_project, "Ctrl+S")
        file_menu.addSeparator()
        export_menu = file_menu.addMenu("Export")
        export_menu.addAction("Export HTML", self.export_html, "Ctrl+E")
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close, "Ctrl+Q")

        edit_menu = menubar.addMenu("✏️ Edit")
        edit_menu.addAction("Undo", self.undo, "Ctrl+Z")
        edit_menu.addAction("Redo", self.redo, "Ctrl+Y")
        edit_menu.addSeparator()
        edit_menu.addAction("Add Section", self._add_section_dialog, "Ctrl+A")

        build_menu = menubar.addMenu("🚀 Build")
        build_menu.addAction("Generate Project", self.generate_project, "Ctrl+G")
        build_menu.addSeparator()
        build_menu.addAction("Preview", self.show_preview, "Ctrl+P")

        tools_menu = menubar.addMenu("🔧 Tools")
        tools_menu.addAction("Deploy Project", self.deploy_project, "Ctrl+D")
        tools_menu.addSeparator()
        tools_menu.addAction("Settings", self.open_settings, "Ctrl+,")

        help_menu = menubar.addMenu("❓ Help")
        help_menu.addAction("Documentation", self.close)

        # ── Toolbar ──
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFixedHeight(50)

        gen_btn = QToolButton()
        gen_btn.setText("🚀 Generate")
        gen_btn.setProperty("primary", True)
        gen_btn.clicked.connect(self.generate_project)
        toolbar.addWidget(gen_btn)

        toolbar.addSeparator()
        preview_btn = QToolButton()
        preview_btn.setText("👁 Preview")
        preview_btn.clicked.connect(self.show_preview)
        toolbar.addWidget(preview_btn)

        toolbar.addSeparator()
        add_btn = QToolButton()
        add_btn.setText("➕ Sections")
        add_btn.clicked.connect(self._add_section_dialog)
        toolbar.addWidget(add_btn)

        export_btn = QToolButton()
        export_btn.setText("💾 Export")
        export_btn.setProperty("primary", True)
        export_btn.clicked.connect(self.export_html)
        toolbar.addWidget(export_btn)

        toolbar.addSeparator()
        settings_btn = QToolButton()
        settings_btn.setText("⚙️ Settings")
        settings_btn.clicked.connect(self.open_settings)
        toolbar.addWidget(settings_btn)

        self.addToolBar(toolbar)

        # ── Main Content ──
        # Tab widget - NO properties tab
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self._create_editor_tab(), "🎨 Editor")
        self.tabs.addTab(self._create_style_tab(), "🎨 Style")
        self.tabs.addTab(self._create_preview_tab(), "👁 Preview")
        layout.addWidget(self.tabs)

        # ── Status Bar ──
        self.statusBar().setStyleSheet("color: #64748b; font-size: 12px;")
        self.project_status = QLabel(" 📐 Ready to build")
        self.statusBar().addPermanentWidget(self.project_status)

    def _create_editor_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # ── Left: Section Library ──
        left = QFrame()
        left.setFixedWidth(280)
        left.setStyleSheet("background: rgba(30, 30, 44, 0.8); border-right: 1px solid rgba(255,255,255,0.06);")
        left_layout = QVBoxLayout(left)
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet("background: rgba(10,10,15,0.8); border-bottom: 1px solid rgba(255,255,255,0.04);")
        header_layout = QHBoxLayout(header)
        header_layout.addWidget(QLabel("📦 Sections"))
        header_layout.addStretch()
        left_layout.addWidget(header)

        search = QLineEdit()
        search.setPlaceholderText("Search sections...")
        search.setFixedHeight(32)
        left_layout.addWidget(search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(4)

        for section_name, section_info in SECTIONS.items():
            btn = QPushButton(f"  {section_info['icon']}  {section_name}")
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px 12px;
                    background: rgba(255,255,255,0.04);
                    color: #e2e8f0;
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 6px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: rgba(59,130,246,0.1);
                    border-color: rgba(59,130,246,0.3);
                }
            """)
            btn.clicked.connect(lambda checked, s=section_name: self._add_section(s))
            content_layout.addWidget(btn)
        content_layout.addStretch()
        scroll.setWidget(content)
        left_layout.addWidget(scroll)
        splitter.addWidget(left)

        # ── Center: Canvas ──
        center = QFrame()
        center.setStyleSheet("background: #0a0a0f;")
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(32, 32, 32, 32)

        canvas_title = QLabel("Canvas")
        canvas_title.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;")
        center_layout.addWidget(canvas_title, alignment=Qt.AlignHCenter)

        self.canvas_area = QScrollArea()
        self.canvas_area.setWidgetResizable(True)
        self.canvas_area.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.canvas_area.setStyleSheet("background: transparent; border: none;")

        self.canvas_frame = QFrame()
        self.canvas_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            }
        """)
        self.canvas_frame.setMinimumWidth(1000)
        self.canvas_layout = QVBoxLayout(self.canvas_frame)
        self.canvas_layout.setContentsMargins(24, 32, 24, 32)
        self.canvas_layout.setSpacing(0)

        self.canvas_empty = QFrame()
        self.canvas_empty.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
                padding: 60px;
                text-align: center;
            }
        """)
        empty_layout = QVBoxLayout(self.canvas_empty)
        empty_icon = QLabel("🎨")
        empty_icon.setStyleSheet("font-size: 64px; color: #94a3b8; opacity: 0.3;")
        empty_layout.addWidget(empty_icon, alignment=Qt.AlignCenter)
        empty_title = QLabel("Ready to build your next project?")
        empty_title.setStyleSheet("color: #64748b; font-size: 20px; font-weight: 600; margin: 16px 0;")
        empty_layout.addWidget(empty_title)
        empty_desc = QLabel("Click \"Generate Project\" to create a complete website, or add sections manually.")
        empty_desc.setStyleSheet("color: #94a3b8; max-width: 400px;")
        empty_layout.addWidget(empty_desc)

        self.canvas_layout.addWidget(self.canvas_empty)
        self.canvas_area.setWidget(self.canvas_frame)
        center_layout.addWidget(self.canvas_area)
        center_layout.addStretch()

        actions = QFrame()
        actions.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 44, 0.6);
                border-radius: 12px;
                margin-top: 16px;
                padding: 0 16px;
            }
        """)
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 8, 0, 8)
        actions_label = QLabel("✨ Ready to build?")
        actions_label.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 500;")
        actions_layout.addWidget(actions_label)
        generate_btn = QPushButton("Generate Project")
        generate_btn.setProperty("pushContent", True)
        generate_btn.setCursor(Qt.PointingHandCursor)
        generate_btn.clicked.connect(self.generate_project)
        actions_layout.addWidget(generate_btn)
        add_btn = QPushButton("Add Section")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_section_dialog)
        actions_layout.addWidget(add_btn)
        actions_layout.addStretch()
        center_layout.addWidget(actions)

        splitter.addWidget(center)
        splitter.setSizes([280, 1000])

        return widget

    def _create_style_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # ── Left: Theme Selection ──
        left = QFrame()
        left.setFixedWidth(320)
        left.setStyleSheet("background: rgba(30, 30, 44, 0.8); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("🎨 Theme Presets")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #f8fafc;")
        left_layout.addWidget(title)

        subtitle = QLabel("Choose a visual style for your project")
        subtitle.setStyleSheet("font-size: 13px; color: #94a3b8; margin-bottom: 16px;")
        left_layout.addWidget(subtitle)

        self.theme_list = QListWidget()
        self.theme_list.addItems(['SaaS', 'Modern Dark', 'Minimal Light', 'Gradient', 'Glassmorphism', 'Neumorphism'])
        self.theme_list.setStyleSheet("""
            QListWidget { background: transparent; border: none; }
            QListWidget::item { padding: 12px 16px; border-radius: 8px; margin-bottom: 4px; color: #cbd5e1; font-size: 14px; }
            QListWidget::item:selected { background: rgba(99, 102, 241, 0.3); color: #f8fafc; }
            QListWidget::item:hover { background: rgba(99, 102, 241, 0.15); }
        """)
        left_layout.addWidget(self.theme_list)

        apply_btn = QPushButton("Apply Theme")
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.setStyleSheet("""
            QPushButton { background: #6366f1; color: white; border: none; border-radius: 8px; padding: 12px; font-weight: 600; }
            QPushButton:hover { background: #818cf8; }
        """)
        apply_btn.clicked.connect(self._apply_theme)
        left_layout.addWidget(apply_btn)

        layout.addWidget(left)

        # ── Right: Live Preview ──
        right = QFrame()
        right.setStyleSheet("background: rgba(30, 30, 44, 0.8); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(20, 20, 20, 20)

        preview_title = QLabel("Live Preview")
        preview_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #f8fafc;")
        right_layout.addWidget(preview_title)

        self.style_preview = QTextEdit()
        self.style_preview.setReadOnly(True)
        self.style_preview.setStyleSheet("background: rgba(10,10,15,0.6); border-radius: 8px; padding: 16px; color: #cbd5e1; font-family: 'Consolas', monospace;")
        self.style_preview.setPlainText("Theme preview will appear here...\n\nSelect a theme and click Apply.")
        right_layout.addWidget(self.style_preview)

        layout.addWidget(right)
        return widget

    def _apply_theme(self):
        theme = self.theme_list.currentItem()
        if not theme:
            return
        theme_name = theme.text()
        if theme_name in STYLE_PRESETS:
            self.project['design'] = STYLE_PRESETS[theme_name].copy()
            self.style_preview.setPlainText(f"Theme '{theme_name}' applied!\n\n{json.dumps(STYLE_PRESETS[theme_name], indent=2)}")
            self.project_status.setText(f"  🎨 Theme applied: {theme_name}")

    def _create_preview_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.render_canvas)
        toolbar.addWidget(refresh_btn)

        export_preview_btn = QPushButton("💾 Export HTML")
        export_preview_btn.setCursor(Qt.PointingHandCursor)
        export_preview_btn.clicked.connect(self.export_html)
        toolbar.addWidget(export_preview_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        preview_wrapper = QFrame()
        preview_wrapper.setStyleSheet("""
            QFrame {
                background: rgba(20, 20, 34, 0.8);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        wrapper_layout = QVBoxLayout(preview_wrapper)

        # Lazy import for headless/offscreen testing
        self.preview_frame = QWebEngineView()
        self.preview_frame.setFixedSize(800, 500)
        wrapper_layout.addWidget(self.preview_frame, alignment=Qt.AlignCenter)

        layout.addWidget(preview_wrapper)
        layout.addStretch()

        return widget

    def render_canvas(self):
        # Clear existing
        for child in self.canvas_frame.children():
            if isinstance(child, QWidget):
                child.deleteLater()

        self.canvas_layout.addWidget(self.canvas_empty)
        self.canvas_empty.hide()

        sections = self.project['pages'][0]['sections']

        if not sections:
            self.canvas_empty.show()
            return

        for section in sections:
            sw = SectionWidget(section['type'], section.get('props', {}))
            sw.setProperty('section-id', section['id'])
            sw.mousePressEvent = lambda e, s=section: self._select_section(s)
            self.canvas_layout.addWidget(sw)

        self.render_properties()
        self.project_status.setText(f"  📐 {len(sections)} sections")

    def _select_section(self, section):
        self.selected_section = section
        self.render_properties()
        self.project_status.setText(f"  👆 Selected: {section['type']}")

    def render_properties(self):
        layout = self.prop_layout if hasattr(self, 'prop_layout') else None
        if not layout:
            return

        for i in range(layout.count()):
            layout.itemAt(i).widget().deleteLater()

        if not self.selected_section:
            empty = QLabel("Select a section to view/edit properties")
            empty.setStyleSheet("color: #64748b; padding: 40px;")
            layout.addWidget(empty)
            return

        section = self.selected_section
        props = section.get('props', {})

        # Editor tab property panel
        header = QFrame()
        header.setFixedHeight(40)
        header.setStyleSheet("background: rgba(30,30,44,0.8); border-bottom: 1px solid rgba(255,255,255,0.05);")
        hlayout = QHBoxLayout(header)
        hlayout.addWidget(QLabel(f"⚙️ Properties — {section['type']}"))
        hlayout.addStretch()
        layout.addWidget(header)

        # Editable properties
        for key, label in [('title', 'Title'), ('subtitle', 'Subtitle'), ('ctaText', 'Button Text'), ('buttonText', 'Button Text')]:
            if key in props:
                label_widget = QLabel(label)
                label_widget.setStyleSheet("color: #94a3b8; font-size: 11px; width: 80px; padding-top: 8px;")
                label_widget.setFixedWidth(80)
                layout.addWidget(label_widget)

                edit = QLineEdit(str(props[key]))
                edit.setStyleSheet("""
                    QLineEdit {
                        background: rgba(10,10,15,0.5);
                        border: 1px solid rgba(255,255,255,0.1);
                        border-radius: 6px;
                        padding: 4px 8px;
                        font-size: 11px;
                    }
                """)
                edit.textChanged.connect(lambda v, k=key: self._update_prop(k, v))
                layout.addWidget(edit)

    def _update_prop(self, key, value):
        if self.selected_section:
            self.selected_section['props'][key] = value
            self.project_status.setText(f"  🔄 Updated: {key}")
            self.save_history()

    def _add_section(self, section_type):
        section = {
            'id': f'section-{random.randint(1000, 9999)}',
            'type': section_type,
            'props': SECTIONS.get(section_type, {'props_template': {}})['props_template'].copy()
        }
        self.project['pages'][0]['sections'].append(section)
        self.selected_section = section
        self.render_canvas()
        self.save_history()
        self.project_status.setText(f"  ➕ Added: {section_type}")
        self.tabs.setCurrentIndex(0)

    def _add_section_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Section")
        dialog.setFixedSize(360, 440)
        dialog.setStyleSheet(STYLESHEET)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)

        search = QLineEdit()
        search.setPlaceholderText("Search sections...")
        search.setStyleSheet("""
            QLineEdit {
                background: rgba(15,23,42,0.6);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
        """)
        layout.addWidget(search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(4)

        for section_name, section_info in SECTIONS.items():
            btn = QPushButton(f"  {section_info['icon']}  {section_name}")
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px 14px;
                    background: rgba(255,255,255,0.04);
                    color: #e2e8f0;
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 8px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: rgba(59,130,246,0.12);
                    border-color: rgba(59,130,246,0.3);
                }
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, s=section_name: (self._add_section(s), dialog.accept()))
            content_layout.addWidget(btn)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

        dialog.exec_()

    def generate_project(self):
        sections_map = {
            'saas': ['Navbar', 'Hero — Centered', 'Features — 3 Columns', 'Stats', 'Pricing — 3 Tiers', 'Testimonials — 2 Columns', 'CTA — Simple', 'Footer'],
            'portfolio': ['Navbar', 'Hero — Split Left', 'Features — Cards', 'Testimonials — 3 Columns', 'Footer'],
            'startup': ['Navbar', 'Hero — Centered', 'Features — 4 Columns', 'Stats', 'Pricing — 2 Tiers', 'Testimonials — 2 Columns', 'FAQ', 'CTA — Split', 'Footer'],
            'agency': ['Navbar', 'Hero — Split Left', 'Features — Cards', 'Stats', 'Testimonials — 3 Columns', 'CTA — Simple', 'Footer'],
            'product': ['Navbar', 'Hero — Minimal', 'Features — 3 Columns', 'Stats', 'Pricing — 3 Tiers', 'Testimonials — 2 Columns', 'CTA — Simple', 'Footer'],
        }
        section_types = sections_map.get('saas', sections_map['saas'])
        sections = []
        for i, stype in enumerate(section_types):
            section = {
                'id': f'section-{i}',
                'type': stype,
                'props': SECTIONS.get(stype, {'props_template': {}})['props_template'].copy()
            }
            sections.append(section)

        self.project['pages'][0]['sections'] = sections
        self.project['name'] = "Generated Landing Page"
        self.render_canvas()
        self.save_history()
        self.project_status.setText(f"  🚀 Generated: {len(sections)} sections")
        self.tabs.setCurrentIndex(0)

    def save_history(self):
        self.history.append(json.dumps(self.project, sort_keys=True))
        if len(self.history) > 100:
            self.history.pop(0)
        self.history_index = len(self.history) - 1

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.project = json.loads(self.history[self.history_index])
            self.render_canvas()
            self.render_properties()

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.project = json.loads(self.history[self.history_index])
            self.render_canvas()
            self.render_properties()

    def export_html(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Export HTML', 'index.html', 'HTML Files (*.html)')
        if path:
            with open(path, 'w') as f:
                f.write('<html><body>Generated by WebBuilder</body></html>')
            self.project_status.setText(f"  💾 Exported to {path}")

    def load_project(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open Project', '', 'JSON Files (*.json)')
        if path:
            try:
                with open(path, 'r') as f:
                    self.project = json.load(f)
                self.render_canvas()
                self.project_status.setText(f"  ✅ Loaded: {Path(path).name}")
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to load project: {e}')

    def save_project(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save Project', '', 'JSON Files (*.json)')
        if path:
            with open(path, 'w') as f:
                json.dump(self.project, f, indent=2)
            self.project_status.setText(f"  💾 Saved to {path}")

    def new_project(self):
        self.project = {
            'id': f'project-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'name': 'Untitled Project',
            'pages': [{'id': 'page-1', 'name': 'Home', 'sections': []}],
            'currentPage': 0,
            'design': STYLE_PRESETS['SaaS'].copy(),
        }
        self.selected_section = None
        self.render_canvas()
        self.project_status.setText("  📐 New project created")

    def show_preview(self):
        QMessageBox.information(self, 'Preview', 'Preview feature coming soon')

    def deploy_project(self):
        QMessageBox.information(self, 'Deploy', 'Choose deployment target:\n• Vercel\n• Netlify\n• Cloudflare')

    def open_settings(self):
        SettingsDialog(self).exec_()

    def closeEvent(self, event):
        if self.history and len(self.history) > 1:
            reply = QMessageBox.question(self, 'Unsaved Changes',
                'You have unsaved changes. Save before closing?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.save_project()
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


# ═══════════════════════════════════════════════════════════════════════════
# SETTINGS DIALOG
# ═══════════════════════════════════════════════════════════════════════════

class SettingsDialog(QDialog):
    """Dedicated Settings Window - opened via Ctrl+, or toolbar button"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Settings")
        self.setMinimumSize(700, 500)
        self.setStyleSheet(STYLESHEET)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QFrame()
        header.setFixedHeight(48)
        header.setStyleSheet("background: rgba(30,30,44,0.8); border-bottom: 1px solid rgba(255,255,255,0.05); border-top-left-radius: 10px; border-top-right-radius: 10px;")
        header_layout = QHBoxLayout(header)
        header_layout.addWidget(QLabel("⚙️ Settings"))
        header_layout.addStretch()
        layout.addWidget(header)

        # Settings tabs
        self.settings_tabs = QTabWidget()
        self.settings_tabs.addTab(self._create_general_tab(), "General")
        self.settings_tabs.addTab(self._create_providers_tab(), "Providers")
        self.settings_tabs.addTab(self._create_model_tab(), "AI Models")
        self.settings_tabs.addTab(self._create_export_tab(), "Export")
        self.settings_tabs.addTab(self._create_about_tab(), "About")
        layout.addWidget(self.settings_tabs)

        layout.addStretch()

    def _create_general_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Appearance section
        section = QFrame()
        section.setStyleSheet("background: rgba(20,20,34,0.6); border-radius: 10px; padding: 12px;")
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(8)

        title = QLabel("🎨 Appearance")
        title.setStyleSheet("color: #e2e8f0; font-weight: 600; font-size: 13px;")
        section_layout.addWidget(title)

        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        theme_layout.addWidget(theme_label)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark (Default)", "Light"])
        self.theme_combo.setStyleSheet("padding: 6px 12px; border-radius: 6px; background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.1); color: #e2e8f0;")
        theme_layout.addWidget(self.theme_combo)
        section_layout.addLayout(theme_layout)

        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Font Size:")
        font_size_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        font_size_layout.addWidget(font_size_label)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 18)
        self.font_size_spin.setValue(13)
        self.font_size_spin.setStyleSheet("padding: 6px 12px; border-radius: 6px; background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.1); color: #e2e8f0;")
        font_size_layout.addWidget(self.font_size_spin)
        section_layout.addLayout(font_size_layout)

        auto_save_layout = QHBoxLayout()
        auto_save_check = QCheckBox("Auto-save projects")
        auto_save_check.setChecked(True)
        auto_save_check.setStyleSheet("color: #e2e8f0;")
        auto_save_layout.addWidget(auto_save_check)
        section_layout.addLayout(auto_save_layout)

        show_line_numbers_layout = QHBoxLayout()
        show_line_numbers_check = QCheckBox("Show line numbers")
        show_line_numbers_check.setChecked(True)
        show_line_numbers_check.setStyleSheet("color: #e2e8f0;")
        show_line_numbers_layout.addWidget(show_line_numbers_check)
        section_layout.addLayout(show_line_numbers_layout)

        layout.addWidget(section)

        # Server section
        section2 = QFrame()
        section2.setStyleSheet("background: rgba(20,20,34,0.6); border-radius: 10px; padding: 12px; margin-top: 12px;")
        section2_layout = QVBoxLayout(section2)
        section2_layout.setSpacing(8)

        title2 = QLabel("🖥️ Server")
        title2.setStyleSheet("color: #e2e8f0; font-weight: 600; font-size: 13px;")
        section2_layout.addWidget(title2)

        port_layout = QHBoxLayout()
        port_label = QLabel("Flask Port:")
        port_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        port_layout.addWidget(port_label)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(5000)
        self.port_spin.setStyleSheet("padding: 6px 12px; border-radius: 6px; background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.1); color: #e2e8f0;")
        port_layout.addWidget(self.port_spin)
        section2_layout.addLayout(port_layout)

        host_layout = QHBoxLayout()
        host_label = QLabel("Host:")
        host_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        host_layout.addWidget(host_label)
        self.host_combo = QComboBox()
        self.host_combo.addItems(["localhost", "0.0.0.0"])
        self.host_combo.setCurrentIndex(0)
        self.host_combo.setStyleSheet("padding: 6px 12px; border-radius: 6px; background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.1); color: #e2e8f0;")
        host_layout.addWidget(self.host_combo)
        section2_layout.addLayout(host_layout)

        auto_refresh_layout = QHBoxLayout()
        auto_refresh_check = QCheckBox("Auto-refresh preview")
        auto_refresh_check.setChecked(True)
        auto_refresh_check.setStyleSheet("color: #e2e8f0;")
        auto_refresh_layout.addWidget(auto_refresh_check)
        section2_layout.addLayout(auto_refresh_layout)

        layout.addWidget(section2)
        layout.addStretch()

        return widget

    def _create_providers_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("🔑 Provider API Keys")
        title.setStyleSheet("color: #e2e8f0; font-weight: 600; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(title)

        desc = QLabel("Enter your API keys. Keys are stored locally and never sent anywhere else.")
        desc.setStyleSheet("color: #64748b; font-size: 12px; margin-bottom: 12px;")
        layout.addWidget(desc)

        # All providers
        providers = [
            ('openai', 'OpenAI', 'https://api.openai.com/api-keys', 'sk-'),
            ('anthropic', 'Anthropic', 'https://console.anthropic.com/settings/keys', 'sk-ant-'),
            ('google', 'Google AI', 'https://aistudio.google.com/apikey', 'AI'),
            ('openrouter', 'OpenRouter', 'https://openrouter.ai/keys', ''),
            ('opencode', 'OpenCode', 'https://opencode.ai/settings/keys', ''),
            ('grok', 'Grok', 'https://console.x.ai/keys', ''),
        ]

        for provider_id, provider_name, url, prefix in providers:
            provider_frame = QFrame()
            provider_frame.setStyleSheet("background: rgba(20,20,34,0.6); border-radius: 10px; padding: 12px; margin-bottom: 8px;")
            provider_layout = QVBoxLayout(provider_frame)
            provider_layout.setSpacing(8)

            provider_header = QHBoxLayout()
            icon_label = QLabel("🔑")
            provider_header.addWidget(icon_label)
            name_label = QLabel(provider_name)
            name_label.setStyleSheet("color: #e2e8f0; font-weight: 600; font-size: 13px;")
            provider_header.addWidget(name_label)
            provider_header.addStretch()
            inline_url = QLabel(f"<a href='{url}' style='color:#3b82f6; text-decoration:none; font-size:11px;'>{url}</a>")
            provider_header.addWidget(inline_url)
            provider_layout.addLayout(provider_header)

            key_layout = QHBoxLayout()
            key_label = QLabel(f"API Key (prefix: {prefix if prefix else 'N/A'}):")
            key_label.setStyleSheet("color: #94a3b8; font-size: 12px; width: 150px;")
            key_layout.addWidget(key_label)
            key_input = QLineEdit()
            key_input.setPlaceholderText(f"Enter {provider_name} API key...")
            key_input.setStyleSheet("""
                QLineEdit {
                    background: rgba(15,23,42,0.5);
                    border: 1px solid rgba(255,255,255,0.12);
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 12px;
                    font-family: monospace;
                }
            """)
            key_layout.addWidget(key_input)
            provider_layout.addLayout(key_layout)

            layout.addWidget(provider_frame)

        layout.addStretch()
        save_btn = QPushButton("Save Keys")
        save_btn.setProperty("primary", True)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.accept)
        layout.addWidget(save_btn)

        return widget

    def _create_model_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("🤖 AI Model Settings")
        title.setStyleSheet("color: #e2e8f0; font-weight: 600; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(title)

        desc = QLabel("Configure which AI provider and model to use for generation.")
        desc.setStyleSheet("color: #64748b; font-size: 12px; margin-bottom: 12px;")
        layout.addWidget(desc)

        # Provider selection
        provider_frame = QFrame()
        provider_frame.setStyleSheet("background: rgba(20,20,34,0.6); border-radius: 10px; padding: 12px;")
        provider_layout = QVBoxLayout(provider_frame)
        provider_layout.setSpacing(8)

        provider_title = QLabel("Provider")
        provider_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;")
        provider_layout.addWidget(provider_title)

        provider_combo_layout = QHBoxLayout()
        provider_combo = QComboBox()
        provider_combo.addItems(['OpenAI', 'Anthropic', 'Google AI', 'OpenRouter', 'OpenCode', 'Grok', 'Local (Ollama)'])
        provider_combo.setCurrentIndex(0)
        provider_combo.setStyleSheet("padding: 8px 12px; border-radius: 8px; background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.12); color: #e2e8f0; font-size: 13px;")
        provider_combo_layout.addWidget(provider_combo)
        provider_layout.addLayout(provider_combo_layout)

        layout.addWidget(provider_frame)

        # Model selection
        model_frame = QFrame()
        model_frame.setStyleSheet("background: rgba(20,20,34,0.6); border-radius: 10px; padding: 12px;")
        model_layout = QVBoxLayout(model_frame)
        model_layout.setSpacing(8)

        model_title = QLabel("Model")
        model_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;")
        model_layout.addWidget(model_title)

        model_combo_layout = QHBoxLayout()
        model_combo = QComboBox()
        model_combo.setCurrentIndex(0)
        model_combo.setStyleSheet("padding: 8px 12px; border-radius: 8px; background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.12); color: #e2e8f0; font-size: 13px;")
        model_combo_layout.addWidget(model_combo)
        model_layout.addLayout(model_combo_layout)

        layout.addWidget(model_frame)

        layout.addStretch()
        apply_btn = QPushButton("Apply Settings")
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.clicked.connect(self.accept)
        layout.addWidget(apply_btn)

        return widget

    def _create_export_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("💾 Export Options")
        title.setStyleSheet("color: #e2e8f0; font-weight: 600; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(title)

        desc = QLabel("Configure how your projects are exported.")
        desc.setStyleSheet("color: #64748b; font-size: 12px; margin-bottom: 12px;")
        layout.addWidget(desc)

        section = QFrame()
        section.setStyleSheet("background: rgba(20,20,34,0.6); border-radius: 10px; padding: 12px;")
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(8)

        export_title = QLabel("Export Format")
        export_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;")
        section_layout.addWidget(export_title)

        export_layout = QHBoxLayout()
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(['HTML5 (Recommended)', 'React Components', 'Vue Components', 'Plain HTML'])
        self.export_format_combo.setCurrentIndex(0)
        self.export_format_combo.setStyleSheet("padding: 8px 12px; border-radius: 8px; background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.12); color: #e2e8f0; font-size: 13px;")
        export_layout.addWidget(self.export_format_combo)
        section_layout.addLayout(export_layout)

        layout.addWidget(section)

        section2 = QFrame()
        section2.setStyleSheet("background: rgba(20,20,34,0.6); border-radius: 10px; padding: 12px; margin-top: 12px;")
        section2_layout = QVBoxLayout(section2)
        section2_layout.setSpacing(8)

        inline_title = QLabel("Code Style")
        inline_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;")
        section2_layout.addWidget(inline_title)

        inline_combo_layout = QHBoxLayout()
        self.inline_style_combo = QComboBox()
        self.inline_style_combo.addItems(['Inline (single file)', 'External (separate CSS/JS)', 'Hybrid'])
        self.inline_style_combo.setCurrentIndex(0)
        self.inline_style_combo.setStyleSheet("padding: 8px 12px; border-radius: 8px; background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.12); color: #e2e8f0; font-size: 13px;")
        inline_combo_layout.addWidget(self.inline_style_combo)
        section2_layout.addLayout(inline_combo_layout)

        minify_layout = QHBoxLayout()
        minify_check = QCheckBox("Minify output")
        minify_check.setChecked(True)
        minify_check.setStyleSheet("color: #e2e8f0;")
        minify_layout.addWidget(minify_check)
        section2_layout.addLayout(minify_layout)

        layout.addWidget(section2)
        layout.addStretch()

        return widget

    def _create_about_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("ℹ️ About WebBuilder Desktop")
        title.setStyleSheet("color: #e2e8f0; font-weight: 600; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(title)

        version_label = QLabel("Version 6.0.0")
        version_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(version_label)

        desc_label = QLabel("WebBuilder Desktop is a professional web builder built with PyQt5. It features neural network-powered color generation, AI-powered content creation, and drag-and-drop section management.")
        desc_label.setStyleSheet("color: #94a3b8; font-size: 12px; line-height: 1.6; margin-bottom: 16px;")
        layout.addWidget(desc_label)

        stats_frame = QFrame()
        stats_frame.setStyleSheet("background: rgba(20,20,34,0.6); border-radius: 10px; padding: 16px;")
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setSpacing(8)

        stats_title = QLabel("📊 Platform Stats")
        stats_title.setStyleSheet("color: #e2e8f0; font-weight: 600; font-size: 12px; margin-bottom: 8px;")
        stats_layout.addWidget(stats_title)

        stats_data = [
            ("Providers", "13"),
            ("Models", "28"),
            ("Free Models", "13"),
            ("Section Types", "16"),
            ("Style Presets", "6"),
        ]

        for stat_name, stat_value in stats_data:
            stat_row = QHBoxLayout()
            stat_row.setSpacing(8)
            stat_name_label = QLabel(stat_name)
            stat_name_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
            stat_row.addWidget(stat_name_label)
            stat_row.addStretch()
            stat_value_label = QLabel(stat_value)
            stat_value_label.setStyleSheet("color: #e2e8f0; font-weight: 600; font-size: 12px;")
            stat_row.addWidget(stat_value_label)
            stats_layout.addLayout(stat_row)

        layout.addWidget(stats_frame)

        layout.addStretch()

        footer = QLabel("Built with ❤️ using PyQt5 and Python")
        footer.setStyleSheet("color: #64748b; font-size: 11px; text-align: center;")
        layout.addWidget(footer)

        return widget


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    window = WebBuilderApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()