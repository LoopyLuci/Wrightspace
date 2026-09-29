"""webbuilder.gui.main_window — Main application window."""

from __future__ import annotations
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QToolBar, QAction, QVBoxLayout, QWidget, QFrame, QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QSplitter, QScrollArea
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter
import sys
import os


class WebBuilderWindow(QMainWindow):
    """Main application window for WebBuilder Desktop."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebBuilder Desktop v6.0")
        self.setMinimumSize(1200, 800)
        
        # Project data
        self.project = {
            "name": "New Project",
            "pages": [{"id": "page-1", "name": "Home", "sections": []}],
            "design": {
                "colors": {"primary": "#3b82f6", "secondary": "#1e293b", "accent": "#8b5cf6", "background": "#0a0a0f", "text": "#e2e8f0"},
                "fonts": {"heading": "Inter", "body": "Inter"},
                "maxWidth": 1200,
                "borderRadius": 8,
                "shadow": "0 4px 6px rgba(0,0,0,0.3)",
            },
            "settings": {"theme": "dark", "autoSave": True, "language": "en"},
        }
        self.selected_section = None
        self.history = []
        self.history_index = -1
        self.undo_stack = []
        self.redo_stack = []
        
        self._init_ui()
        self._create_toolbar()
        self._setup_menu()
        self._create_tabs()
    
    def _init_ui(self):
        """Initialize the main window UI."""
        self.setStyleSheet("""
            QMainWindow { background: #0a0a0f; color: #e2e8f0; }
            QTabBar::tab { 
                padding: 14px 24px; background: transparent; color: #64748b;
                border: none; border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected { 
                color: #3b82f6; border-bottom: 2px solid #3b82f6;
                background: rgba(59,130,246,0.08);
            }
            QTabWidget::pane { 
                background: #0a0a0f; border-top: 1px solid rgba(255,255,255,0.05);
            }
            QToolBar { 
                background: rgba(30,30,44,0.95); border: none;
                border-bottom: 1px solid rgba(255,255,255,0.05);
                padding: 6px 12px; spacing: 12px;
            }
            QToolButton { 
                background: rgba(255,255,255,0.06); color: #e2e8f0;
                border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;
                padding: 8px 16px; font-weight: 500; font-size: 12px;
            }
            QToolButton:hover { background: rgba(255,255,255,0.12); }
            QToolButton[primary="true"] { 
                background: #3b82f6; color: white; border-color: #3b82f6;
                box-shadow: 0 4px 12px rgba(59,130,246,0.3);
            }
            QToolButton[primary="true"]:hover { background: #2563eb; }
            QPushButton { 
                background: rgba(255,255,255,0.06); color: #e2e8f0;
                border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.12); }
            QPushButton[primary="true"] {
                background: #3b82f6; color: white; border: none;
                padding: 10px 20px; font-weight: 600; font-size: 14px;
                border-radius: 10px;
            }
            QLineEdit, QComboBox, QSpinBox, QTextEdit {
                background: rgba(15,23,42,0.4); color: #e2e8f0;
                border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;
                padding: 8px 12px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #3b82f6; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: #1e293b; border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
            }
            QCheckBox { color: #e2e8f0; }
            QCheckBox::indicator {
                width: 18px; height: 18px;
                border: 1px solid rgba(255,255,255,0.2); border-radius: 4px;
                background: rgba(255,255,255,0.05);
            }
            QCheckBox::indicator:checked {
                background: #3b82f6; border-color: #3b82f6;
            }
            QSpinBox { 
                background: rgba(15,23,42,0.4); color: #e2e8f0;
                border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;
                padding: 8px 12px; font-size: 13px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background: rgba(255,255,255,0.1); border: none; border-radius: 4px;
                width: 20px; height: 20px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: rgba(255,255,255,0.2);
            }
            QScrollArea { border: none; }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.05); width: 8px; border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255,255,255,0.2); border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background: rgba(255,255,255,0.3); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0; background: none;
            }
            QMenuBar { 
                background: rgba(30,41,59,0.95); color: #cbd5e1;
                border-bottom: 1px solid #334155; padding: 0 16px; font-weight: 500;
            }
            QMenuBar::item { padding: 6px 12px; border-radius: 6px; margin: 2px 1px; }
            QMenuBar::item:selected { background: #3b82f6; color: white; }
            QMenu { 
                background: #1e293b; color: #f8fafc; border: 1px solid #334155; padding: 4px;
            }
            QMenu::item { padding: 6px 12px; border-radius: 4px; }
            QMenu::item:selected { background: #334155; color: #f8fafc; }
            QDockWidget { 
                background: rgba(30,41,59,0.95); color: #cbd5e1;
                border: none; border-left: 1px solid #334155;
            }
            QDockWidget::title { 
                background: rgba(30,41,59,0.95); padding: 8px 12px;
                border-bottom: 1px solid #334155; font-weight: 500;
            }
            QStatusBar { background: rgba(30,41,59,0.95); color: #94a3b8; font-size: 12px; }
        """)
    
    def _create_toolbar(self):
        """Create the main toolbar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)
        
        actions = [
            ("New", "Ctrl+N", self._new_project),
            ("Open", "Ctrl+O", self._open_project),
            ("Save", "Ctrl+S", self._save_project),
            ("Export HTML", "Ctrl+E", self._export_html),
            ("Preview", "Ctrl+P", self._preview),
            ("Settings", "Ctrl+,", self._open_settings),
        ]
        
        for text, shortcut, callback in actions:
            action = QAction(text, self)
            action.setShortcut(shortcut)
            action.triggered.connect(callback)
            toolbar.addAction(action)
        
        toolbar.addSeparator()
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self._undo)
        toolbar.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self._redo)
        toolbar.addAction(redo_action)
        
        toolbar.addSeparator()
        
        gen_btn = QPushButton("🚀 Generate Project")
        gen_btn.setProperty("primary", True)
        gen_btn.setFixedHeight(36)
        gen_btn.clicked.connect(self._generate_project)
        toolbar.addWidget(gen_btn)
        
        self.toolbar = toolbar
    
    def _setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("New Project\tCtrl+N", self._new_project)
        file_menu.addAction("Open Project\tCtrl+O", self._open_project)
        file_menu.addAction("Save Project\tCtrl+S", self._save_project)
        file_menu.addSeparator()
        file_menu.addAction("Export HTML\tCtrl+E", self._export_html)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction("Undo\tCtrl+Z", self._undo)
        edit_menu.addAction("Redo\tCtrl+Y", self._redo)
        edit_menu.addSeparator()
        edit_menu.addAction("Generate Content", self._generate_content)
        edit_menu.addAction("AI Suggest", self._ai_suggest)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction("Preview\tCtrl+P", self._preview)
        view_menu.addAction("Toggle Chat Panel", self._toggle_chat)
        view_menu.addAction("Toggle Properties Panel", self._toggle_properties)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction("Theme Picker", self._show_theme_picker)
        tools_menu.addAction("Color Palette", self._show_color_palette)
        tools_menu.addAction("Settings", self._open_settings)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("About", self._show_about)
    
    def _create_tabs(self):
        """Create the editor and preview tabs."""
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setTabsClosable(False)
        
        # Editor tab
        editor_tab = QWidget()
        editor_layout = QVBoxLayout(editor_tab)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        
        # Splitter for canvas and properties
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([600, 300])
        splitter.setMinimumWidth(400)
        
        # Canvas frame
        self.canvas_frame = QFrame()
        self.canvas_frame.setObjectName("canvas_frame")
        self.canvas_layout = QVBoxLayout(self.canvas_frame)
        self.canvas_layout.setContentsMargins(0, 0, 0, 0)
        self.canvas_layout.setSpacing(0)
        
        # Section list
        self.section_list = QScrollArea()
        self.section_list.setWidgetResizable(True)
        self.section_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.section_widget = QWidget()
        self.section_layout = QVBoxLayout(self.section_widget)
        self.section_list.setWidget(self.section_widget)
        self.canvas_layout.addWidget(self.section_list)
        
        # Properties panel placeholder
        self.properties_frame = QFrame()
        self.properties_frame.setObjectName("properties_frame")
        self.properties_layout = QVBoxLayout(self.properties_frame)
        self.properties_layout.setContentsMargins(16, 16, 16, 16)
        
        props_title = QLabel("Properties")
        props_title.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;")
        self.properties_layout.addWidget(props_title)
        
        props_empty = QLabel("Select a section to edit its properties")
        props_empty.setStyleSheet("color: #475569; font-size: 14px;")
        props_empty.setAlignment(Qt.AlignCenter)
        self.properties_layout.addWidget(props_empty)
        self.properties_empty_label = props_empty
        
        # Chat panel placeholder
        self.chat_frame = QFrame()
        self.chat_frame.setObjectName("chat_frame")
        self.chat_layout = QVBoxLayout(self.chat_frame)
        self.chat_layout.setContentsMargins(12, 12, 12, 12)
        
        chat_title = QLabel("💬 AI Chat")
        chat_title.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;")
        self.chat_layout.addWidget(chat_title)
        
        chat_placeholder = QLabel("Chat panel is available as a standalone window.\nOpen from View menu or press Ctrl+Shift+C")
        chat_placeholder.setStyleSheet("color: #475569; font-size: 12px;")
        chat_placeholder.setAlignment(Qt.AlignCenter)
        self.chat_layout.addWidget(chat_placeholder)
        
        self.chat_frame.setVisible(False)
        
        splitter.addWidget(self.canvas_frame)
        splitter.addWidget(self.properties_frame)
        
        editor_layout.addWidget(splitter)
        
        # Bottom bar for chat
        bottom_splitter = QSplitter(Qt.Horizontal)
        bottom_splitter.addWidget(self.chat_frame)
        bottom_splitter.setStretchFactor(0, 1)
        bottom_splitter.setVisible(False)
        
        editor_layout.addWidget(bottom_splitter)
        editor_layout.setStretch(0, 1)
        
        self.editor_tab = editor_tab
        self.main_splitter = splitter
        self.bottom_splitter = bottom_splitter
        
        # Preview tab
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("preview_frame")
        self.preview_layout = QVBoxLayout(self.preview_frame)
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        
        # Preview content
        preview_label = QLabel("Preview")
        preview_label.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600;")
        self.preview_layout.addWidget(preview_label)
        
        self.preview_content = QLabel("No project to preview yet.\nGenerate or load a project first.")
        self.preview_content.setStyleSheet("color: #475569; font-size: 14px;")
        self.preview_content.setAlignment(Qt.AlignCenter)
        self.preview_layout.addWidget(self.preview_content)
        
        preview_layout.addWidget(self.preview_frame)
        
        self.preview_tab = preview_tab
        self.preview_html = ""
        
        self.tabs.addTab(editor_tab, "✏️  Editor")
        self.tabs.addTab(preview_tab, "👁️  Preview")
        self.tabs.setCurrentIndex(0)
        
        self.setCentralWidget(self.tabs)
    
    def _toggle_chat(self):
        """Toggle the chat panel visibility."""
        self.chat_frame.setVisible(not self.chat_frame.isVisible())
    
    def _toggle_properties(self):
        """Toggle the properties panel visibility."""
        self.properties_frame.setVisible(not self.properties_frame.isVisible())
    
    def _update_undo_redo_buttons(self):
        """Update undo/redo button states."""
        for action in self.toolbar.actions():
            if action.text() == "Undo":
                action.setEnabled(len(self.undo_stack) > 0)
            elif action.text() == "Redo":
                action.setEnabled(len(self.redo_stack) > 0)
    
    # ── Project Operations ──────────────────────────────────────────────
    
    def _new_project(self):
        """Create a new project."""
        self.project = {
            "name": "New Project",
            "pages": [{"id": "page-1", "name": "Home", "sections": []}],
            "design": {
                "colors": {"primary": "#3b82f6", "secondary": "#1e293b", "accent": "#8b5cf6", "background": "#0a0a0f", "text": "#e2e8f0"},
                "fonts": {"heading": "Inter", "body": "Inter"},
                "maxWidth": 1200,
                "borderRadius": 8,
                "shadow": "0 4px 6px rgba(0,0,0,0.3)",
            },
            "settings": {"theme": "dark", "autoSave": True, "language": "en"},
        }
        self.selected_section = None
        self.history = []
        self.history_index = -1
        self.undo_stack = []
        self.redo_stack = []
        self._render_canvas()
        self._update_status("New project created")
    
    def _open_project(self):
        """Open a project file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "WebBuilder Projects (*.json);;All Files (*)"
        )
        if file_path:
            try:
                import json
                with open(file_path, 'r') as f:
                    self.project = json.load(f)
                self.selected_section = None
                self.history = []
                self.history_index = -1
                self.undo_stack = []
                self.redo_stack = []
                self._render_canvas()
                self._update_status(f"Project loaded: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to open project: {str(e)}")
    
    def _save_project(self):
        """Save the current project."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "WebBuilder Projects (*.json);;All Files (*)"
        )
        if file_path:
            try:
                import json
                with open(file_path, 'w') as f:
                    json.dump(self.project, f, indent=2)
                self._update_status(f"Project saved: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save project: {str(e)}")
    
    def _export_html(self):
        """Export the project as HTML."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export HTML", "", "HTML Files (*.html);;All Files (*)"
        )
        if file_path:
            try:
                from webbuilder.export import HTMLExporter
                exporter = HTMLExporter()
                html = exporter.generate(self.project)
                with open(file_path, 'w') as f:
                    f.write(html)
                self._update_status(f"Exported to: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export: {str(e)}")
    
    def _preview(self):
        """Show preview tab."""
        self.tabs.setCurrentIndex(1)
    
    def _open_settings(self):
        """Open settings dialog."""
        from webbuilder.gui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    # ── Canvas Rendering ────────────────────────────────────────────────
    
    def _render_canvas(self):
        """Render the canvas with current project sections."""
        # Clear existing widgets
        while self.section_layout.count():
            item = self.section_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        
        if not sections:
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.setAlignment(Qt.AlignCenter)
            
            icon = QLabel("🎨")
            icon.setAlignment(Qt.AlignCenter)
            icon.setStyleSheet("font-size: 48px;")
            empty_layout.addWidget(icon)
            
            title = QLabel("Ready to Build?")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("color: #64748b; font-size: 20px; font-weight: bold; margin-top: 16px;")
            empty_layout.addWidget(title)
            
            subtitle = QLabel("Click 'Generate Full Project' or 'Pick Template' to get started")
            subtitle.setAlignment(Qt.AlignCenter)
            subtitle.setStyleSheet("color: #475569; font-size: 14px; margin-top: 8px;")
            empty_layout.addWidget(subtitle)
            
            btn_layout = QHBoxLayout()
            btn_layout.setAlignment(Qt.AlignCenter)
            
            gen_btn = QPushButton("🚀 Generate Full Project")
            gen_btn.setStyleSheet("background: #3b82f6; color: white; padding: 12px 24px; border-radius: 8px; font-weight: bold; margin-top: 24px;")
            gen_btn.clicked.connect(self._generate_project)
            btn_layout.addWidget(gen_btn)
            
            empty_layout.addLayout(btn_layout)
            self.section_layout.addWidget(empty_widget)
            return
        
        colors = self.project.get("design", {}).get("colors", {})
        
        for section in sections:
            widget = self._make_section_widget(section, colors)
            self.section_layout.addWidget(widget)
    
    def _make_section_widget(self, section: dict, colors: dict) -> QFrame:
        """Create a widget for a section."""
        frame = QFrame()
        frame.setCursor(Qt.PointingHandCursor)
        
        props = section.get("props", {})
        section_type = section.get("type", "")
        
        is_selected = section.get("id") == self.selected_section
        
        if is_selected:
            frame.setStyleSheet(f"border: 2px solid #3b82f6; border-radius: 4px; background: rgba(59,130,246,0.05);")
        else:
            frame.setStyleSheet("border: 2px solid transparent; border-radius: 4px;")
        
        def on_click(e):
            self._select_section(section["id"])
        
        frame.mousePressEvent = lambda e: on_click(e)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        
        content = self._make_section_content(section_type, props, colors)
        layout.addWidget(content)
        
        return frame
    
    def _make_section_content(self, section_type: str, props: dict, colors: dict) -> QWidget:
        """Create content widget for a section type."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        
        if "hero" in section_type.lower():
            widget.setStyleSheet(f'background: {props.get("backgroundColor", colors.get("primary", "#3b82f6"))}; padding: 80px 40px;')
            layout = QVBoxLayout(widget)
            layout.setAlignment(Qt.AlignCenter)
            
            title = QLabel(props.get("title", "Welcome"))
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
            layout.addWidget(title)
            
            subtitle = QLabel(props.get("subtitle", ""))
            subtitle.setAlignment(Qt.AlignCenter)
            subtitle.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 18px; margin-top: 12px;")
            layout.addWidget(subtitle)
            
            cta = QPushButton(props.get("ctaText", "Get Started"))
            cta.setStyleSheet("background: white; color: #1e293b; padding: 12px 24px; border-radius: 8px; font-weight: 600; max-width: 200px;")
            layout.addWidget(cta, alignment=Qt.AlignCenter)
        
        elif "features" in section_type.lower():
            widget.setStyleSheet("background: white; padding: 60px 40px;")
            layout = QVBoxLayout(widget)
            
            title = QLabel(props.get("title", "Features"))
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("color: #1e293b; font-size: 28px; font-weight: bold; margin-bottom: 32px;")
            layout.addWidget(title)
            
            items = props.get("items", [])
            grid = QHBoxLayout()
            grid.setSpacing(16)
            
            for item in items[:4]:
                card = QFrame()
                card.setStyleSheet("background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;")
                card_layout = QVBoxLayout(card)
                
                icon = QLabel(item.get("icon", "🔹"))
                icon.setAlignment(Qt.AlignCenter)
                icon.setStyleSheet("font-size: 24px;")
                card_layout.addWidget(icon)
                
                card_title = QLabel(item.get("title", "Feature"))
                card_title.setAlignment(Qt.AlignCenter)
                card_title.setStyleSheet("color: #1e293b; font-weight: 600; font-size: 14px;")
                card_layout.addWidget(card_title)
                
                desc = QLabel(item.get("description", ""))
                desc.setAlignment(Qt.AlignCenter)
                desc.setStyleSheet("color: #64748b; font-size: 12px;")
                card_layout.addWidget(desc)
                
                grid.addWidget(card)
            
            layout.addLayout(grid)
        
        elif "pricing" in section_type.lower():
            widget.setStyleSheet("background: #f8fafc; padding: 60px 40px;")
            layout = QVBoxLayout(widget)
            
            title = QLabel(props.get("title", "Pricing"))
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("color: #1e293b; font-size: 28px; font-weight: bold; margin-bottom: 32px;")
            layout.addWidget(title)
            
            tiers = props.get("tiers", [])
            grid = QHBoxLayout()
            grid.setSpacing(16)
            
            for tier in tiers[:3]:
                card = QFrame()
                card.setStyleSheet("background: white; border: 2px solid #e2e8f0; border-radius: 12px; padding: 24px;")
                card_layout = QVBoxLayout(card)
                
                name = QLabel(tier.get("name", "Plan"))
                name.setAlignment(Qt.AlignCenter)
                name.setStyleSheet("color: #1e293b; font-weight: 600; font-size: 16px;")
                card_layout.addWidget(name)
                
                price = QLabel(tier.get("price", "$0"))
                price.setAlignment(Qt.AlignCenter)
                price.setStyleSheet("color: #1e293b; font-size: 32px; font-weight: bold; margin: 8px 0;")
                card_layout.addWidget(price)
                
                grid.addWidget(card)
            
            layout.addLayout(grid)
        
        elif "cta" in section_type.lower():
            widget.setStyleSheet(f'background: {props.get("backgroundColor", colors.get("primary", "#3b82f6"))}; padding: 60px 40px;')
            layout = QVBoxLayout(widget)
            layout.setAlignment(Qt.AlignCenter)
            
            title = QLabel(props.get("title", "Ready to Get Started?"))
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
            layout.addWidget(title)
            
            btn = QPushButton(props.get("buttonText", "Sign Up"))
            btn.setStyleSheet("background: white; color: #3b82f6; padding: 12px 24px; border-radius: 8px; font-weight: 600; max-width: 200px;")
            layout.addWidget(btn, alignment=Qt.AlignCenter)
        
        elif "stats" in section_type.lower():
            widget.setStyleSheet("background: white; padding: 60px 40px;")
            layout = QVBoxLayout(widget)
            
            title = QLabel(props.get("title", "Our Numbers"))
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("color: #1e293b; font-size: 28px; font-weight: bold; margin-bottom: 32px;")
            layout.addWidget(title)
            
            items = props.get("items", [])
            grid = QHBoxLayout()
            
            for item in items[:4]:
                item_layout = QVBoxLayout()
                value = QLabel(item.get("value", "0"))
                value.setAlignment(Qt.AlignCenter)
                value.setStyleSheet("color: #3b82f6; font-size: 32px; font-weight: bold;")
                item_layout.addWidget(value)
                
                label = QLabel(item.get("label", ""))
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("color: #64748b; font-size: 14px;")
                item_layout.addWidget(label)
                
                grid.addLayout(item_layout)
            
            layout.addLayout(grid)
        
        elif "testimonials" in section_type.lower():
            widget.setStyleSheet("background: #f8fafc; padding: 60px 40px;")
            layout = QVBoxLayout(widget)
            
            title = QLabel(props.get("title", "What Our Customers Say"))
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("color: #1e293b; font-size: 28px; font-weight: bold; margin-bottom: 32px;")
            layout.addWidget(title)
            
            items = props.get("items", [])
            grid = QHBoxLayout()
            grid.setSpacing(16)
            
            for item in items[:3]:
                card = QFrame()
                card.setStyleSheet("background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px;")
                card_layout = QVBoxLayout(card)
                
                quote = QLabel(f'"{item.get("quote", "")}"')
                quote.setStyleSheet("font-style: italic; color: #64748b; margin-bottom: 12px;")
                card_layout.addWidget(quote)
                
                author = QLabel(f'- {item.get("author", "")}')
                author.setStyleSheet("color: #1e293b; font-weight: 600;")
                card_layout.addWidget(author)
                
                grid.addWidget(card)
            
            layout.addLayout(grid)
        
        elif "faq" in section_type.lower():
            widget.setStyleSheet("background: white; padding: 60px 40px;")
            layout = QVBoxLayout(widget)
            
            title = QLabel(props.get("title", "Frequently Asked Questions"))
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("color: #1e293b; font-size: 28px; font-weight: bold; margin-bottom: 32px;")
            layout.addWidget(title)
            
            items = props.get("items", [])
            for item in items[:6]:
                q = QLabel(f"Q: {item.get('question', '')}")
                q.setStyleSheet("color: #1e293b; font-weight: 600; font-size: 14px; margin-top: 16px;")
                layout.addWidget(q)
                
                a = QLabel(f"A: {item.get('answer', '')}")
                a.setStyleSheet("color: #64748b; font-size: 13px; margin-left: 16px;")
                layout.addWidget(a)
        
        elif "footer" in section_type.lower():
            widget.setStyleSheet(f'background: {props.get("backgroundColor", colors.get("secondary", "#1e293b"))}; padding: 40px;')
            layout = QVBoxLayout(widget)
            layout.setAlignment(Qt.AlignCenter)
            
            copyright = QLabel(props.get("copyright", "© 2024 Company Name. All rights reserved."))
            copyright.setAlignment(Qt.AlignCenter)
            copyright.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 14px;")
            layout.addWidget(copyright)
        
        else:
            widget.setStyleSheet("background: #1e293b; padding: 20px; border-radius: 8px;")
            layout = QVBoxLayout(widget)
            layout.setAlignment(Qt.AlignCenter)
            
            label = QLabel(f"[{section_type}] - Custom Section")
            label.setStyleSheet("color: #94a3b8; font-size: 14px;")
            layout.addWidget(label)
        
        return widget
    
    def _select_section(self, section_id: str):
        """Select a section and update properties panel."""
        self.selected_section = section_id
        self._render_canvas()
        self._render_properties()
    
    def _render_properties(self):
        """Render the properties panel for the selected section."""
        while self.properties_layout.count():
            item = self.properties_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        props_title = QLabel("Properties")
        props_title.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;")
        self.properties_layout.addWidget(props_title)
        
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        selected_section = None
        
        for section in sections:
            if section.get("id") == self.selected_section:
                selected_section = section
                break
        
        if not selected_section:
            empty = QLabel("Select a section to edit its properties")
            empty.setStyleSheet("color: #475569; font-size: 14px;")
            empty.setAlignment(Qt.AlignCenter)
            self.properties_layout.addWidget(empty)
            self.properties_empty_label = empty
            return
        
        self.properties_empty_label = None
        
        props = selected_section.get("props", {})
        section_type = selected_section.get("type", "")
        
        # Section type
        type_label = QLabel(f"Type: {section_type}")
        type_label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500;")
        type_label.setAlignment(Qt.AlignCenter)
        self.properties_layout.addWidget(type_label)
        
        self.properties_layout.addSpacing(16)
        
        # Build property editors based on section type
        if "hero" in section_type.lower():
            self._add_prop_editor("title", "Title", props.get("title", ""), str)
            self._add_prop_editor("subtitle", "Subtitle", props.get("subtitle", ""), str)
            self._add_prop_editor("ctaText", "CTA Text", props.get("ctaText", ""), str)
            colors = self.project.get("design", {}).get("colors", {})
            self._add_color_picker("backgroundColor", "Background", props.get("backgroundColor", colors.get("primary", "#3b82f6")))
        
        elif "features" in section_type.lower():
            self._add_prop_editor("title", "Title", props.get("title", "Features"), str)
            
            items = props.get("items", [])
            for i, item in enumerate(items[:4]):
                item_group = QFrame()
                item_group.setStyleSheet("background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px; margin-bottom: 8px;")
                item_layout = QVBoxLayout(item_group)
                
                item_title = QLabel(f"Feature {i + 1}")
                item_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600;")
                item_layout.addWidget(item_title)
                
                title_editor = QLineEdit(item.get("title", ""))
                title_editor.setPlaceholderText("Title")
                title_editor.textChanged.connect(lambda t, idx=i: self._update_feature_title(idx, t))
                item_layout.addWidget(title_editor)
                
                desc_editor = QLineEdit(item.get("description", ""))
                desc_editor.setPlaceholderText("Description")
                desc_editor.textChanged.connect(lambda t, idx=i: self._update_feature_desc(idx, t))
                item_layout.addWidget(desc_editor)
                
                self.properties_layout.addWidget(item_group)
        
        elif "pricing" in section_type.lower():
            self._add_prop_editor("title", "Title", props.get("title", "Pricing"), str)
            
            tiers = props.get("tiers", [])
            for i, tier in enumerate(tiers[:3]):
                tier_group = QFrame()
                tier_group.setStyleSheet("background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px; margin-bottom: 8px;")
                tier_layout = QVBoxLayout(tier_group)
                
                tier_title = QLabel(f"Tier {i + 1}")
                tier_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600;")
                tier_layout.addWidget(tier_title)
                
                name_editor = QLineEdit(tier.get("name", ""))
                name_editor.setPlaceholderText("Tier Name")
                name_editor.textChanged.connect(lambda t, idx=i: self._update_tier_name(idx, t))
                tier_layout.addWidget(name_editor)
                
                price_editor = QLineEdit(tier.get("price", ""))
                price_editor.setPlaceholderText("Price")
                price_editor.textChanged.connect(lambda t, idx=i: self._update_tier_price(idx, t))
                tier_layout.addWidget(price_editor)
                
                self.properties_layout.addWidget(tier_group)
        
        elif "cta" in section_type.lower():
            self._add_prop_editor("title", "Title", props.get("title", "Ready?"), str)
            self._add_prop_editor("buttonText", "Button Text", props.get("buttonText", "Sign Up"), str)
            colors = self.project.get("design", {}).get("colors", {})
            self._add_color_picker("backgroundColor", "Background", props.get("backgroundColor", colors.get("primary", "#3b82f6")))
        
        elif "stats" in section_type.lower():
            self._add_prop_editor("title", "Title", props.get("title", "Our Numbers"), str)
            
            items = props.get("items", [])
            for i, item in enumerate(items[:4]):
                stat_group = QFrame()
                stat_group.setStyleSheet("background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px; margin-bottom: 8px;")
                stat_layout = QVBoxLayout(stat_group)
                
                stat_title = QLabel(f"Stat {i + 1}")
                stat_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600;")
                stat_layout.addWidget(stat_title)
                
                value_editor = QLineEdit(item.get("value", ""))
                value_editor.setPlaceholderText("Value")
                value_editor.textChanged.connect(lambda t, idx=i: self._update_stat_value(idx, t))
                stat_layout.addWidget(value_editor)
                
                label_editor = QLineEdit(item.get("label", ""))
                label_editor.setPlaceholderText("Label")
                label_editor.textChanged.connect(lambda t, idx=i: self._update_stat_label(idx, t))
                stat_layout.addWidget(label_editor)
                
                self.properties_layout.addWidget(stat_group)
        
        elif "testimonials" in section_type.lower():
            self._add_prop_editor("title", "Title", props.get("title", "Testimonials"), str)
            
            items = props.get("items", [])
            for i, item in enumerate(items[:3]):
                test_group = QFrame()
                test_group.setStyleSheet("background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px; margin-bottom: 8px;")
                test_layout = QVBoxLayout(test_group)
                
                test_title = QLabel(f"Testimonial {i + 1}")
                test_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600;")
                test_layout.addWidget(test_title)
                
                quote_editor = QLineEdit(item.get("quote", ""))
                quote_editor.setPlaceholderText("Quote")
                quote_editor.textChanged.connect(lambda t, idx=i: self._update_testimonial_quote(idx, t))
                test_layout.addWidget(quote_editor)
                
                author_editor = QLineEdit(item.get("author", ""))
                author_editor.setPlaceholderText("Author Name")
                author_editor.textChanged.connect(lambda t, idx=i: self._update_testimonial_author(idx, t))
                test_layout.addWidget(author_editor)
                
                self.properties_layout.addWidget(test_group)
        
        elif "faq" in section_type.lower():
            self._add_prop_editor("title", "Title", props.get("title", "FAQ"), str)
            
            items = props.get("items", [])
            for i, item in enumerate(items[:6]):
                faq_group = QFrame()
                faq_group.setStyleSheet("background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px; margin-bottom: 8px;")
                faq_layout = QVBoxLayout(faq_group)
                
                faq_title = QLabel(f"FAQ Item {i + 1}")
                faq_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600;")
                faq_layout.addWidget(faq_title)
                
                q_editor = QLineEdit(item.get("question", ""))
                q_editor.setPlaceholderText("Question")
                q_editor.textChanged.connect(lambda t, idx=i: self._update_faq_question(idx, t))
                faq_layout.addWidget(q_editor)
                
                a_editor = QLineEdit(item.get("answer", ""))
                a_editor.setPlaceholderText("Answer")
                a_editor.textChanged.connect(lambda t, idx=i: self._update_faq_answer(idx, t))
                faq_layout.addWidget(a_editor)
                
                self.properties_layout.addWidget(faq_group)
        
        elif "footer" in section_type.lower():
            self._add_prop_editor("copyright", "Copyright", props.get("copyright", ""), str)
            colors = self.project.get("design", {}).get("colors", {})
            self._add_color_picker("backgroundColor", "Background", props.get("backgroundColor", colors.get("secondary", "#1e293b")))
        
        else:
            custom_label = QLabel("Custom section - limited editing available")
            custom_label.setStyleSheet("color: #64748b; font-size: 13px;")
            self.properties_layout.addWidget(custom_label)
        
        # Delete section button
        self.properties_layout.addSpacing(16)
        delete_btn = QPushButton("🗑️  Delete Section")
        delete_btn.setStyleSheet("background: rgba(239,68,68,0.1); color: #ef4444; border: 1px solid rgba(239,68,68,0.2); border-radius: 8px; padding: 8px 16px;")
        delete_btn.clicked.connect(self._delete_selected_section)
        self.properties_layout.addWidget(delete_btn)
        
        self.properties_layout.addStretch()
    
    def _add_prop_editor(self, key: str, label: str, value: str, field_type: type = str):
        """Add a property editor to the properties panel."""
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 500;")
        self.properties_layout.addWidget(label_widget)
        
        if field_type == str:
            editor = QLineEdit(value)
            editor.setPlaceholderText(label)
            editor.textChanged.connect(lambda t, k=key: self._update_prop(k, t))
            self.properties_layout.addWidget(editor)
        elif field_type == int:
            editor = QSpinBox()
            editor.setValue(int(value) if value else 0)
            editor.setRange(0, 10000)
            editor.valueChanged.connect(lambda v, k=key: self._update_prop(k, str(v)))
            self.properties_layout.addWidget(editor)
        
        self.properties_layout.addSpacing(8)
    
    def _add_color_picker(self, key: str, label: str, value: str):
        """Add a color picker to the properties panel."""
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 500;")
        self.properties_layout.addWidget(label_widget)
        
        color_widget = QFrame()
        color_widget.setFixedSize(40, 40)
        color_widget.setStyleSheet(f"""
            QFrame {{
                background: {value};
                border: 2px solid rgba(255,255,255,0.2);
                border-radius: 8px;
            }}
        """)
        
        def on_click(e):
            from PyQt5.QtWidgets import QColorDialog
            color = QColorDialog.getColor(QColor(value), self, "Select Color")
            if color.isValid():
                hex_color = color.name()
                self._update_prop(key, hex_color)
        
        color_widget.mousePressEvent = lambda e: on_click(e)
        self.properties_layout.addWidget(color_widget, alignment=Qt.AlignCenter)
        
        hex_label = QLabel(value)
        hex_label.setStyleSheet("color: #64748b; font-size: 11px; font-family: monospace;")
        self.properties_layout.addWidget(hex_label, alignment=Qt.AlignCenter)
        
        self.properties_layout.addSpacing(12)
    
    def _update_prop(self, key: str, value: str):
        """Update a property value."""
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        
        for section in sections:
            if section.get("id") == self.selected_section:
                section["props"][key] = value
                break
        
        self._save_history()
        self._render_canvas()
    
    def _update_feature_title(self, index: int, value: str):
        """Update a feature item title."""
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        
        for section in sections:
            if section.get("id") == self.selected_section:
                items = section["props"].get("items", [])
                if index < len(items):
                    items[index]["title"] = value
                break
        
        self._save_history()
        self._render_canvas()
    
    def _update_feature_desc(self, index: int, value: str):
        """Update a feature item description."""
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        
        for section in sections:
            if section.get("id") == self.selected_section:
                items = section["props"].get("items", [])
                if index < len(items):
                    items[index]["description"] = value
                break
        
        self._save_history()
        self._render_canvas()
    
    def _update_tier_name(self, index: int, value: str):
        """Update a pricing tier name."""
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        
        for section in sections:
            if section.get("id") == self.selected_section:
                tiers = section["props"].get("tiers", [])
                if index < len(tiers):
                    tiers[index]["name"] = value
                break
        
        self._save_history()
        self._render_canvas()
    
    def _update_tier_price(self, index: int, value: str):
        """Update a pricing tier price."""
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        
        for section in sections:
            if section.get("id") == self.selected_section:
                tiers = section["props"].get("tiers", [])
                if index < len(tiers):
                    tiers[index]["price"] = value
                break
        
        self._save_history()
        self._render_canvas()
    
    def _update_stat_value(self, index: int, value: str):
        """Update a stat value."""
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        
        for section in sections:
            if section.get("id") == self.selected_section:
                items = section["props"].get("items", [])
                if index < len(items):
                    items[index]["value"] = value
                break
        
        self._save_history()
        self._render_canvas()
    
    def _update_stat_label(self, index: int, value: str):
        """Update a stat label."""
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        
        for section in sections:
            if section.get("id") == self.selected_section:
                items = section["props"].get("items", [])
                if index < len(items):
                    items[index]["label"] = value
                break
        
        self._save_history()
        self._render_canvas()
    
    def _update_testimonial_quote(self, index: int, value: str):
        """Update a testimonial quote."""
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        
        for section in sections:
            if section.get("id") == self.selected_section:
                items = section["props"].get("items", [])
                if index < len(items):
                    items[index]["quote"] = value
                break
        
        self._save_history()
        self._render_canvas()
    
    def _update_testimonial_author(self, index: int, value: str):
        """Update a testimonial author."""
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        
        for section in sections:
            if section.get("id") == self.selected_section:
                items = section["props"].get("items", [])
                if index < len(items):
                    items[index]["author"] = value
                break
        
        self._save_history()
        self._render_canvas()
    
    def _update_faq_question(self, index: int, value: str):
        """Update an FAQ question."""
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        
        for section in sections:
            if section.get("id") == self.selected_section:
                items = section["props"].get("items", [])
                if index < len(items):
                    items[index]["question"] = value
                break
        
        self._save_history()
        self._render_canvas()
    
    def _update_faq_answer(self, index: int, value: str):
        """Update an FAQ answer."""
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        
        for section in sections:
            if section.get("id") == self.selected_section:
                items = section["props"].get("items", [])
                if index < len(items):
                    items[index]["answer"] = value
                break
        
        self._save_history()
        self._render_canvas()
    
    # ── Section Management ──────────────────────────────────────────────
    
    def _add_section(self, section_type: str):
        """Add a new section to the project."""
        colors = self.project.get("design", {}).get("colors", {})
        
        # Generate default props based on section type
        props = {}
        
        if "hero" in section_type.lower():
            props = {
                "title": "Welcome to Your Site",
                "subtitle": "Build something amazing with WebBuilder",
                "ctaText": "Get Started",
                "backgroundColor": colors.get("primary", "#3b82f6"),
            }
        elif "features" in section_type.lower():
            props = {
                "title": "Features",
                "items": [
                    {"icon": "⚡", "title": "Fast", "description": "Lightning fast performance"},
                    {"icon": "🔒", "title": "Secure", "description": "Enterprise-grade security"},
                    {"icon": "🎨", "title": "Beautiful", "description": "Stunning designs"},
                    {"icon": "📱", "title": "Responsive", "description": "Works on all devices"},
                ],
            }
        elif "pricing" in section_type.lower():
            props = {
                "title": "Pricing",
                "tiers": [
                    {"name": "Basic", "price": "$9/month"},
                    {"name": "Pro", "price": "$29/month"},
                    {"name": "Enterprise", "price": "$99/month"},
                ],
            }
        elif "cta" in section_type.lower():
            props = {
                "title": "Ready to Get Started?",
                "buttonText": "Sign Up Now",
                "backgroundColor": colors.get("primary", "#3b82f6"),
            }
        elif "stats" in section_type.lower():
            props = {
                "title": "Our Numbers",
                "items": [
                    {"value": "10K+", "label": "Customers"},
                    {"value": "50M+", "label": "Downloads"},
                    {"value": "99.9%", "label": "Uptime"},
                    {"value": "4.9★", "label": "Rating"},
                ],
            }
        elif "testimonials" in section_type.lower():
            props = {
                "title": "What Our Customers Say",
                "items": [
                    {"quote": "This product changed my workflow completely.", "author": "Sarah Johnson"},
                    {"quote": "Best investment I've made for my business.", "author": "Mike Chen"},
                    {"quote": "Incredible quality and support.", "author": "Emily Davis"},
                ],
            }
        elif "faq" in section_type.lower():
            props = {
                "title": "Frequently Asked Questions",
                "items": [
                    {"question": "How does it work?", "answer": "Simply drag and drop elements to build your page."},
                    {"question": "Is it free?", "answer": "Yes, WebBuilder has a free tier for personal projects."},
                    {"question": "Can I export my work?", "answer": "Absolutely! Export to HTML, React, or static sites."},
                    {"question": "Is there support?", "answer": "We offer 24/7 support via email and chat."},
                ],
            }
        elif "footer" in section_type.lower():
            props = {
                "copyright": f"© {__import__('datetime').datetime.now().year} Your Company. All rights reserved.",
                "backgroundColor": colors.get("secondary", "#1e293b"),
            }
        else:
            props = {
                "title": "Section",
                "content": "Custom section content",
            }
        
        section = {
            "id": f"sec-{len(self.project['pages'][0]['sections'])}",
            "type": section_type,
            "props": props,
        }
        
        self.project["pages"][0]["sections"].append(section)
        self.selected_section = section["id"]
        self._save_history()
        self._render_canvas()
        self._render_properties()
        self._update_status(f"Added {section_type}")
    
    def _add_section_dialog(self):
        """Show dialog to add a section."""
        from webbuilder.gui.section_dialog import SectionDialog
        dialog = SectionDialog(self)
        if dialog.exec_():
            section_type = dialog.get_selected_type()
            if section_type:
                self._add_section(section_type)
    
    def _delete_selected_section(self):
        """Delete the currently selected section."""
        if not self.selected_section:
            return
        
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        
        for i, section in enumerate(sections):
            if section.get("id") == self.selected_section:
                sections.pop(i)
                break
        
        self.selected_section = None
        self._save_history()
        self._render_canvas()
        self._render_properties()
        self._update_status("Section deleted")
    
    # ── History / Undo/Redo ─────────────────────────────────────────────
    
    def _save_history(self):
        """Save current state to history."""
        import json
        state = json.dumps(self.project, indent=2)
        
        # Remove any redo states if we're not at the end
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
            self.redo_stack = []
        
        self.history.append(state)
        self.history_index = len(self.history) - 1
        
        # Keep max 50 history states
        if len(self.history) > 50:
            self.history.pop(0)
            self.history_index = len(self.history) - 1
    
    def _undo(self):
        """Undo the last action."""
        if self.history_index > 0:
            self.history_index -= 1
            import json
            self.project = json.loads(self.history[self.history_index])
            self.selected_section = None
            self._render_canvas()
            self._render_properties()
            self._update_status("Undo")
    
    def _redo(self):
        """Redo the last undone action."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            import json
            self.project = json.loads(self.history[self.history_index])
            self.selected_section = None
            self._render_canvas()
            self._render_properties()
            self._update_status("Redo")
    
    # ── Content Generation ──────────────────────────────────────────────
    
    def _generate_content(self):
        """Generate content for the selected section using AI."""
        if not self.selected_section:
            self._update_status("Select a section first")
            return
        
        sections = self.project.get("pages", [{}])[0].get("sections", [])
        
        for section in sections:
            if section["id"] == self.selected_section:
                if "title" in section["props"]:
                    # Generate better content
                    hero_content = self._generate_hero_content()
                    section["props"]["title"] = hero_content["title"]
                    section["props"]["subtitle"] = hero_content["subtitle"]
                
                self._save_history()
                self._render_canvas()
                self._render_properties()
                self._update_status("Content generated")
                return
        
        self._update_status("No editable section selected")
    
    def _generate_hero_content(self) -> dict:
        """Generate hero section content."""
        company_name = self.project.get("name", "Your Company")
        
        return {
            "title": f"Build Something Amazing with {company_name}",
            "subtitle": "Create professional websites in minutes with our powerful drag-and-drop builder.",
        }
    
    def _ai_suggest(self):
        """Show AI suggestions for improving the project."""
        import random
        suggestions = [
            "💡 Add a Testimonials section to build trust with visitors",
            "💡 Your hero section could have a stronger call-to-action",
            "💡 Consider adding social proof below your features section",
            "💡 A pricing table would help convert visitors into customers",
            "💡 Add an FAQ section to address common questions",
            "💡 Your page needs more visual hierarchy and spacing",
            "💡 Try a contrasting color for your CTA button",
            "💡 Add a countdown timer for urgency if selling something",
        ]
        
        suggestion = random.choice(suggestions)
        self._update_status(suggestion)
    
    # ── Theme / Design ───────────────────────────────────────────────────
    
    def _show_theme_picker(self):
        """Show theme picker dialog."""
        from webbuilder.gui.theme_dialog import ThemeDialog
        dialog = ThemeDialog(self)
        if dialog.exec_():
            theme = dialog.get_selected_theme()
            if theme:
                self._apply_theme(theme)
    
    def _apply_theme(self, theme: dict):
        """Apply a theme to the project."""
        self.project["design"]["colors"] = theme.get("colors", self.project["design"]["colors"])
        self.project["design"]["fonts"] = theme.get("fonts", self.project["design"]["fonts"])
        self.project["design"]["borderRadius"] = theme.get("borderRadius", 8)
        
        self._render_canvas()
        self._update_status(f"Theme applied: {theme.get('name', 'Custom')}")
    
    def _show_color_palette(self):
        """Show color palette generator."""
        from webbuilder.gui.color_palette_dialog import ColorPaletteDialog
        dialog = ColorPaletteDialog(self)
        if dialog.exec_():
            palette = dialog.get_selected_palette()
            if palette:
                self.project["design"]["colors"].update(palette)
                self._render_canvas()
                self._update_status("Color palette updated")
    
    # ── Status & About ───────────────────────────────────────────────────
    
    def _update_status(self, message: str):
        """Update the status bar message."""
        self.statusBar().showMessage(message)
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About WebBuilder",
            "<html><body style='font-family: Inter, sans-serif; color: #e2e8f0;'>"
            "<h2 style='color: #3b82f6;'>WebBuilder Desktop v6.0</h2>"
            "<p>Premium Edition — Professional Website Builder</p>"
            "<p style='margin-top: 16px;'>Build production-ready websites with drag-and-drop simplicity.</p>"
            "<p style='margin-top: 16px; color: #64748b; font-size: 12px;'>"
            "© 2024 WebBuilder. All rights reserved.</p>"
            "</body></html>"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        self._update_status("Goodbye!")
        event.accept()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = WebBuilderWindow()
    window.show()
    sys.exit(app.exec_())
