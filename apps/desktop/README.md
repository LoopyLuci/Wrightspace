# WebBuilder Desktop

A professional web building platform with AI assistance, drag-and-drop canvas, live preview, and 7 ML models trained from scratch.

## ✨ Key Features

### Visual Editor
- Drag-and-drop canvas with 16+ section types
- Auto-Layout ML model for optimal positioning
- Live preview with responsive breakpoints
- Section reordering, duplication, and deletion

### AI-Powered Design
- **Color Harmony ML**: WCAG-compliant palette generation
- **Typography Pairing ML**: Optimal font combinations
- **Layout Generation ML**: Grid positioning and spacing
- **Page Speed ML**: Load time and Lighthouse score prediction
- **Accessibility ML**: WCAG 2.1 violation detection
- **Code Completion ML**: HTML/CSS/JS token prediction
- **User Intent ML**: Next-action prediction for proactive UI

### Code Editor
- Syntax highlighting for HTML/CSS/JS/PHP
- Code folding, multi-cursor, snippets
- Find/replace with regex
- DOM panel, tag selector, split view

### AI Chat Assistant
- Markdown rendering with code blocks
- Conversation history with timestamps
- Model selector (13+ AI models, free first)
- Temperature control, token counting
- Export conversations to JSON/text

### Form Builder
- Visual drag-and-drop form designer
- 10 field types (text, email, select, textarea, number, checkbox, radio, file, date, tel)
- Property editor for labels, placeholders, validation
- Live HTML preview, save to canvas

### SEO Tools
- Meta tags, JSON-LD structured data
- XML sitemap generation
- Robots.txt generator
- Visual SEO dashboard with score gauge
- Accessibility compliance checker

### Multi-Format Export
- HTML (standalone)
- React (components + package.json)
- Vue (SFC components)
- JSON (project data)
- Python/PyQt5 (generated code)

### Project Browser
- Visual project cards with search/sort
- Open, duplicate, delete projects
- Preview thumbnails, section counts
- Keyboard shortcuts (Ctrl+O)

### Theme System
- 6 built-in themes (Dark, Light, Midnight, Forest, Sunset, Ocean)
- Runtime switching (no restart)
- Full Qt stylesheet generation

### Hardware Acceleration
- CPU/GPU detection (NVIDIA, AMD, Apple Metal, Intel)
- Multi-threaded task queue
- Memory monitoring with leak detection

## 🤖 AI Providers

| Provider | Models | Free Tier |
|----------|--------|-----------|
| OpenAI | GPT-4o, GPT-4o Mini | ✅ Mini |
| Anthropic | Claude 3.5 Sonnet/Haiku | ✅ Haiku |
| OpenRouter | 50+ models | ✅ Many |
| xAI Grok | Grok-2 | ❌ |
| Nous Research | Hermes, Caption | ✅ |
| Ollama | Local models | ✅ All |
| LM Studio | Local models | ✅ All |

## 🚀 Quick Start

```bash
# Install
pip install -e .

# Train ML models (optional, improves AI features)
python -m webbuilder.ml_engine.train_all

# Launch GUI
python webbuilder_desktop.py

# Build distribution
python do_build.py
```

## 📁 Architecture

```
webbuilder/
├── core/           # Zero-dependency foundation (100-year durability)
├── gui/            # PyQt5 desktop interface (~4000 lines)
│   ├── __init__.py # Main window, canvas, chat, settings
│   ├── chat_panel.py # Enhanced AI chat with markdown/bubbles
│   ├── form_builder_dialog.py # Visual form designer
│   └── feedback_dialog.py # User feedback collection
├── ml_engine/      # 7 ML models from scratch (NumPy)
│   ├── __init__.py # Dense, Dropout, BatchNorm, Conv2D, LSTM
│   ├── models.py   # Color, Speed, Layout, Typography, A11y, Code, Intent
│   ├── data.py     # Synthetic data generation
│   ├── training.py # Training pipeline with gradient clipping
│   └── persistence.py # Save/load trained weights
├── generative_ui/  # Self-modifying interface engine
│   ├── __init__.py # UINode, MutationEngine, AgentCommandParser
│   ├── themes.py   # 6 themes with runtime switching
│   ├── widget_factory.py # 25+ widget types from schemas
│   ├── code_generator.py # HTML/React/Vue/Python export
│   └── virtual_list.py # 100k+ item rendering
├── export/         # Multi-format exporters
├── ai/             # 7 AI provider integrations (live model discovery)
├── code_editor/    # Syntax highlighting, snippets, DOM panel
├── css_designer/   # Visual CSS designer
├── templates/      # 6 pre-built templates
├── forms/          # Form builder
├── seo/            # SEO analysis, sitemap, robots.txt
├── hardware/       # CPU/GPU detection, thread pool
├── plugins/        # Plugin development kit
├── contrib/        # CMS, E-Commerce, Publishing, Collaboration
└── agentic/        # Agentic building infrastructure

tests/              # 246 tests (100% passing)
├── unit/           # ML engine, core modules
├── integration/    # Full workflow tests
├── security/       # XSS, injection prevention
└── performance/    # Speed benchmarks
```

## 🧠 ML Models

All models are built from scratch using only NumPy (no external ML frameworks):

| Model | Architecture | Training | Accuracy |
|-------|--------------|----------|----------|
| Color Harmony | 33→48→96→48→15 | 5000 samples, 20 epochs | MSE: 0.085 |
| Page Speed | 5→32→64→32→2 | 5000 samples, 20 epochs | MSE: 0.084 |
| Layout Gen | 33→64→128→64→130 | 5000 samples, 20 epochs | MSE: 0.092 |
| Typography | 45→64→128→64→100 | 5000 samples, 20 epochs | MSE: 0.088 |
| Accessibility | 280→128→64→30 | 5000 samples, 20 epochs | MSE: 0.090 |
| Code Complete | 20→128→256→128→1000 | 504 samples, 10 epochs | Cross-entropy |
| User Intent | 324→128→64→50 | 5000 samples, 20 epochs | MSE: 0.086 |

## 📊 Test Coverage

- **246 tests** total, all passing
- **Unit tests**: ML layers, models, persistence, data generation
- **Integration tests**: Project lifecycle, form workflows, search
- **Security tests**: XSS prevention, input sanitization, path traversal
- **Performance tests**: Export speed, project save/load

## 🏗️ Distribution

### Executable (PyInstaller)
```bash
python do_build.py
# Output: dist/WebBuilder.exe (~50 MB)
```

### Portable ZIP
```bash
# Run build.py for ZIP packaging
python build.py --zip
```

### Windows Installer (NSIS)
```bash
# Requires NSIS installed
makensis installer.nsi
# Output: dist/WebBuilder-Setup.exe
```

## 📝 License

MIT License - Free for personal and commercial use.

## 🔗 Links

- GitHub: https://github.com/LoopLuci/WebBuilder
- Documentation: https://hermes-agent.nousresearch.com/docs
- Issues: https://github.com/LoopLuci/WebBuilder/issues

---

Built with Python, PyQt5, and NumPy. No external ML frameworks.
