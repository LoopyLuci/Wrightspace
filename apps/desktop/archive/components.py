#!/usr/bin/env python3
"""
WebBuilder Desktop v4.0 — Premium Professional App Builder
Part 2: GUI components (continues from desktop_app.py)
"""

import sys
import os
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Config is provided by desktop_app.py - no import needed here


# ============================================================================
# STYLES
# ============================================================================

STYLESHEET = """
* {
    font-family: 'Segoe UI', 'Inter', system-ui, -apple-system, sans-serif;
    font-size: 14px;
}

QMainWindow {
    background: #0f172a;
    color: #f8fafc;
}

QMenuBar {
    background: rgba(30, 41, 59, 0.95);
    color: #cbd5e1;
    border-bottom: 1px solid #334155;
    padding: 0 16px;
    font-weight: 500;
}

QMenuBar::item {
    padding: 6px 12px;
    border-radius: 6px;
    margin: 2px 1px;
}

QMenuBar::item:selected {
    background: #3b82f6;
    color: white;
}

QMenu {
    background: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    padding: 4px;
}

QMenu::item {
    padding: 6px 12px;
    border-radius: 4px;
}

QMenu::item:selected {
    background: #334155;
    color: #f8fafc;
}

QToolBar {
    background: rgba(30, 41, 59, 0.95);
    border-bottom: 1px solid #334155;
    padding: 4px 8px;
    spacing: 8px;
}

QTabWidget::pane {
    border: none;
    background: #0f172a;
}

QTabBar::tab {
    background: #1e293b;
    color: #94a3b8;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left: 6px;
    border-top-right: 6px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background: #3b82f6;
    color: white;
}

QDockWidget {
    background: #1e293b;
}

QDockWidget::title {
    background: #1e293b;
    color: #f8fafc;
    padding: 4px 8px;
    font-weight: 600;
    border-bottom: 1px solid #334155;
}

QPushButton {
    background: #334155;
    color: #f8fafc;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 500;
    transition: all 0.2s ease;
}

QPushButton:hover {
    background: #475569;
}

QPushButton:pressed {
    background: #475569;
}

QPushButton.primary {
    background: #3b82f6;
    color: white;
    border: none;
}

QPushButton.primary:hover {
    background: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59,130,246,0.3);
}

QPushButton.success {
    background: #10b981;
    color: white;
    border: none;
}

QPushButton.success:hover {
    background: #059669;
}

QPushButton.danger {
    background: #ef4444;
    color: white;
    border: none;
}

QPushButton.danger:hover {
    background: #dc2626;
}

QPushButton.flat {
    background: transparent;
    border: none;
    color: #94a3b8;
    padding: 4px 8px;
}

QPushButton.flat:hover {
    background: rgba(255,255,255,0.05);
    color: #f8fafc;
}

QLineEdit, QTextEdit, QComboBox, QPlainTextEdit {
    background: #0f172a;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-color: #3b82f6;
}

QComboBox::drop-down {
    border: none;
    background: transparent;
}

QComboBox::down-arrow {
    color: #64748b;
}

QScrollArea {
    border: none;
    background: transparent;
}

QSplitter::handle {
    background: #334155;
    width: 2px;
}

QStatusBar {
    background: #1e293b;
    border-top: 1px solid #334155;
    color: #94a3b8;
    padding: 4px 8px;
}

QLabel.section-header {
    color: #f8fafc;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 8px 12px 4px;
}

QLabel.category-label {
    color: #64748b;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 12px 0 4px 4px;
}

QGroupBox {
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 20px;
}

QGroupBox::title {
    padding: 0 8px;
    color: #94a3b8;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QListWidget {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    outline: none;
}

QListWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #1e293b;
}

QListWidget::item:selected {
    background: #3b82f6;
    color: white;
}

QListWidget::item:hover {
    background: #334155;
}

QTabBar {
    background: transparent;
}

QTabBar::tab {
    padding: 8px 16px;
    background: #334155;
    color: #94a3b8;
    border-top-left: 6px;
    border-top-right: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: #3b82f6;
    color: white;
}

QTabBar::tab:!selected {
    margin-bottom: -2px;
}

QTabWidget#providersTabWidget QTabBar {
    alignment: left;
}
"""


# ============================================================================
# CUSTOM WIDGETS
# ============================================================================

class SectionWidget(QFrame):
    """A draggable section widget for the canvas"""
    
    def __init__(self, section, parent=None):
        super().__init__(parent)
        self.section = section
        self.setStyleSheet("""
            SectionWidget {
                background: white;
                border: 2px solid transparent;
                border-radius: 4px;
                margin: 4px 0;
            }
            SectionWidget.selected {
                border-color: #3b82f6;
            }
        """)
        self.setProperty("selected", False)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        header = QHBoxLayout()
        
        icon = QLabel("📄")
        icon.setStyleSheet("font-size: 16px;")
        header.addWidget(icon)
        
        title = QLabel(section['type'].replace('-', ' ').title())
        title.setStyleSheet("font-weight: 600; color: #1e293b;")
        header.addWidget(title)
        
        header.addStretch()
        
        type_label = QLabel("section")
        type_label.setStyleSheet("font-size: 10px; color: #64748b; background: #f1f5f9; padding: 2px 8px; border-radius: 10px;")
        header.addWidget(type_label)
        
        layout.addLayout(header)
        
        props = section.get('props', {})
        if 'title' in props:
            title_label = QLabel(props['title'])
            title_label.setStyleSheet("font-size: 14px; color: #334155; margin-top: 4px;")
            title_label.setWordWrap(True)
            layout.addWidget(title_label)
        
        drop_btn = QPushButton("⋮")
        drop_btn.setFixedSize(20, 20)
        drop_btn.setStyleSheet("QPushButton { background: transparent; border: none; color: #94a3b8; font-size: 12px; } QPushButton:hover { color: #f8fafc; }")
        layout.addWidget(drop_btn)
        
        self.mousePressEvent = self._on_click
    
    def _on_click(self, event):
        self.setProperty("selected", True)
        self.style().polish(self)
        self.update()
    
    def select(self, selected):
        self.setProperty("selected", selected)
        self.style().polish(self)
        self.update()


class ProviderCard(QFrame):
    """A beautiful provider card for the API keys section"""
    
    def __init__(self, provider_id, provider_info, has_key=False, parent=None):
        super().__init__(parent)
        self.provider_id = provider_id
        self.provider_info = provider_info
        self.has_key = has_key
        
        self.setFixedHeight(140)
        self.setStyleSheet("""
            ProviderCard {
                background: #1e293b;
                border: 2px solid #334155;
                border-radius: 12px;
                padding: 16px;
            }
            ProviderCard.has-key {
                border-color: #10b981;
                background: rgba(16, 185, 129, 0.1);
            }
            ProviderCard.not-configured {
                border-color: #ef4444;
                background: rgba(239, 68, 68, 0.05);
            }
        """)
        
        if self.has_key:
            self.setProperty("has_key", True)
        elif provider_info.get('type') == 'local':
            self.setProperty("not_configured", False)
        else:
            self.setProperty("not_configured", True)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Icon
        icon_label = QLabel(provider_info['icon'])
        icon_label.setStyleSheet("font-size: 32px;")
        layout.addWidget(icon_label)
        
        # Info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(f"<b>{provider_info['name']}</b>")
        name_label.setStyleSheet("font-size: 16px; color: #f8fafc;")
        info_layout.addWidget(name_label)
        
        type_label = QLabel(provider_info.get('type', 'cloud').title())
        type_label.setStyleSheet("font-size: 11px; color: #64748b; text-transform: uppercase;")
        info_layout.addWidget(type_label)
        
        pricing_label = QLabel("Free" if provider_info.get('pricing', False) == 'free' else "Paid")
        pricing_label.setStyleSheet("font-size: 10px; color: #94a3b8;")
        info_layout.addWidget(pricing_label)
        
        model_count = len(provider_info.get('models', []))
        models_label = QLabel(f"{model_count} models")
        models_label.setStyleSheet("font-size: 10px; color: #64748b;")
        info_layout.addWidget(models_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Status
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        
        if self.has_key:
            status_dot = QLabel("🟢")
            status_text = QLabel("Configured")
        elif provider_info.get('type') == 'local':
            status_dot = QLabel("🔵")
            status_text = QLabel("Local")
        else:
            status_dot = QLabel("⚪")
            status_text = QLabel("Not configured")
        
        status_dot.setStyleSheet("font-size: 12px;")
        status_text.setStyleSheet("font-size: 11px; color: #94a3b8;")
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_text)
        
        layout.addWidget(status_widget)


class ModelSelector(QFrame):
    """Beautiful model selection widget with free models first"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            ModelSelector {
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        self.provider_combo = QComboBox()
        self.provider_combo.setFixedHeight(36)
        self.provider_combo.setStyleSheet("""
            QComboBox {
                background: #0f172a;
                color: #f8fafc;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 6px 12px;
            }
        """)
        layout.addWidget(self.provider_combo)
        
        self.model_list = QListWidget()
        self.model_list.setStyleSheet("""
            QListWidget {
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 6px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #1e293b;
            }
            QListWidget::item:selected {
                background: #3b82f6;
                color: white;
            }
        """)
        layout.addWidget(self.model_list)
    
    def set_providers(self, providers):
        self.provider_combo.clear()
        for pid, info in providers.items():
            self.provider_combo.addItem(f"{info['icon']} {info['name']}", pid)
    
    def update_models(self, provider_id, models_data):
        self.model_list.clear()
        
        # Sort: free/local first, then by context size
        sorted_models = sorted(models_data, key=lambda m: (
            not m.get('free', False),
            -m.get('context', 0)
        ))
        
        for model in sorted_models:
            item = QListWidgetItem()
            widget = QWidget()
            layout = QVBoxLayout()
            
            top_row = QHBoxLayout()
            name = QLabel(f"<b>{model['name']}</b>")
            name.setStyleSheet("color: #f8fafc;")
            
            tags = QHBoxLayout()
            if model.get('free'):
                tag = QLabel("FREE")
                tag.setStyleSheet("font-size: 8px; background: #10b981; color: white; padding: 1px 6px; border-radius: 3px;")
                tags.addWidget(tag)
            
            badge = QLabel("Local" if model.get('free') and model.get('context', 0) < 64000 else "Cloud")
            badge.setStyleSheet(f"font-size: 8px; background: {'#6366f1' if model.get('context', 0) < 64000 else '#3b82f6'}; color: white; padding: 1px 6px; border-radius: 3px;")
            tags.addWidget(badge)
            
            top_row.addWidget(name)
            top_row.addLayout(tags)
            top_row.addStretch()
            
            context_label = QLabel(f"{model.get('context', 'N/A'):,} ctx")
            context_label.setStyleSheet("font-size: 10px; color: #64748b;")
            top_row.addWidget(context_label)
            
            layout.addLayout(top_row)
            
            desc = QLabel(model.get('description', ''))
            desc.setStyleSheet("font-size: 10px; color: #94a3b8;")
            desc.setWordWrap(True)
            layout.addWidget(desc)
            
            widget.setLayout(layout)
            
            item.setSizeHint(widget.sizeHint())
            self.model_list.addItem(item)
            self.model_list.setItemWidget(item, widget)


class LoadingSpinner(QLabel):
    """Animated loading indicator"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("font-size: 20px;")
        self.setAlignment(Qt.AlignCenter)
        
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.frame_idx = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(80)
    
    def next_frame(self):
        self.setText(self.frames[self.frame_idx])
        self.frame_idx = (self.frame_idx + 1) % len(self.frames)
    
    def start(self):
        self.timer.start(80)
        self.show()
    
    def stop(self):
        self.timer.stop()
        self.hide()


# Export custom widgets
__all__ = [
    'STYLESHEET',
    'SectionWidget',
    'ProviderCard',
    'ModelSelector',
    'LoadingSpinner',
]
