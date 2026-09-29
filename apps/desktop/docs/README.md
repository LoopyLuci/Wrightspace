# WebBuilder Desktop — User Documentation

> **Version 1.0.0** | Last updated: August 2026

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Your First Project](#your-first-project)
4. [Features](#features)
5. [Templates](#templates)
6. [AI Assistant](#ai-assistant)
7. [Exporting Your Site](#exporting-your-site)
8. [Keyboard Shortcuts](#keyboard-shortcuts)
9. [FAQ](#faq)
10. [Support](#support)

---

## Quick Start

### What is WebBuilder?

WebBuilder is a **desktop web builder** that lets you create beautiful websites without coding. Drag and drop sections, customize with AI assistance, and export production-ready HTML, React, or Vue code.

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Windows 10 (64-bit) | Windows 11 |
| RAM | 4 GB | 8 GB |
| Disk Space | 500 MB | 1 GB |
| Internet | Required for AI features | Broadband |

### First Launch

1. Run `WebBuilder.exe`
2. Choose a template or start from scratch
3. Add sections from the library
4. Customize with the property inspector
5. Export when ready

---

## Installation

### Option 1: Installer (Recommended)

1. Download `WebBuilder-Setup.exe`
2. Run the installer
3. Follow the prompts
4. Launch from Start Menu or Desktop shortcut

### Option 2: Portable (No Installation)

1. Download `WebBuilder-Portable-v1.0.0.zip`
2. Extract to any folder
3. Run `WebBuilder.exe`

### Uninstall

- **Installer**: Add/Remove Programs → WebBuilder → Uninstall
- **Portable**: Delete the folder

---

## Your First Project

### Step 1: Create a New Project

```
File → New from Template... (Ctrl+Shift+N)
```

Choose a template:
- **SaaS Landing Page** — Software products
- **Creative Portfolio** — Designers, photographers
- **Online Store** — E-commerce
- **Restaurant & Cafe** — Food businesses
- **Digital Agency** — Service companies
- **Blog & Magazine** — Content creators

### Step 2: Add Sections

In the **left panel**, click any section to add it to your canvas:

| Section | Purpose |
|---------|---------|
| Navbar | Navigation header |
| Hero — Centered | Main headline, centered |
| Hero — Split Left | Headline with image |
| Hero — Minimal | Simple text-only hero |
| Features — 3/4 Columns | Feature grid |
| Features — Cards | Feature cards |
| CTA — Simple | Call-to-action banner |
| CTA — Split | CTA with image |
| Pricing — 3/2 Tiers | Pricing table |
| Stats | Statistics display |
| Testimonials — 2/3 Columns | Customer quotes |
| FAQ | Frequently asked questions |
| Footer | Page footer |

### Step 3: Customize

Click any section on the canvas to edit its properties in the **right panel**:

- **Text**: Click to edit titles, descriptions, button text
- **Colors**: Use color pickers for backgrounds, text, accents
- **Images**: Enter image URLs
- **Links**: Add navigation links

### Step 4: Preview

Click the **Preview tab** to see your site live. Use the device toggles:

- 📱 Mobile (375px)
- 📱 Tablet (768px)
- 🖥 Desktop (1280px)

### Step 5: Export

```
File → Export HTML (Ctrl+E)
```

Choose format:
- **HTML** — Standalone website
- **React** — React components
- **Vue** — Vue.js SFC
- **JSON** — Structured data

---

## Features

### Visual Editor

| Feature | Description |
|---------|-------------|
| Drag-and-Drop | Add sections by clicking |
| Live Preview | See changes instantly |
| Responsive Preview | Test all device sizes |
| Undo/Redo | Ctrl+Z / Ctrl+Y |

### Property Inspector

Edit section properties:

- **Text fields**: Single-line text
- **Text areas**: Multi-line text
- **Numbers**: Numeric inputs
- **Checkboxes**: Boolean toggles
- **Color pickers**: Visual color selection
- **Lists**: Add/remove items

### AI Assistant

The AI chat panel can:

- Generate sections from descriptions
- Suggest design improvements
- Write content for your pages
- Answer web design questions

**Example prompts:**
- "Create a hero section for a fitness app"
- "Add a pricing table with 3 tiers"
- "Write compelling copy for a SaaS landing page"

### Templates

6 professional templates included:

1. **SaaS Landing Page** — Software products
2. **Creative Portfolio** — Designers, photographers
3. **Online Store** — E-commerce
4. **Restaurant & Cafe** — Food businesses
5. **Digital Agency** — Service companies
6. **Blog & Magazine** — Content creators

### Export Formats

| Format | Use Case |
|--------|----------|
| HTML | Static hosting, any server |
| React | React applications |
| Vue | Vue.js applications |
| JSON | Data interchange, backups |

---

## Templates

### Using Templates

1. `File → New from Template...` (Ctrl+Shift+N)
2. Browse categories or search
3. Click a template to preview
4. Click "Use Template"

### Template Categories

- **Business** — SaaS, Agency
- **Creative** — Portfolio
- **E-commerce** — Online Store
- **Food & Drink** — Restaurant
- **Content** — Blog

### Creating Custom Templates

1. Build a project you want to reuse
2. `File → Export JSON`
3. Save to `~/.webbuilder/templates/`
4. Restart WebBuilder

---

## AI Assistant

### Setup

The AI assistant requires API keys:

| Provider | Environment Variable |
|----------|---------------------|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Ollama | Local, no key needed |

### Setting API Keys

**Windows:**
1. Search "Environment Variables" in Start
2. Click "Environment Variables"
3. Under "User variables", click "New"
4. Enter variable name and value
5. Restart WebBuilder

### Using AI

1. Select a model from the dropdown
2. Type your request
3. Press Enter or click Send
4. AI-generated sections appear on canvas

### AI Capabilities

- **Section generation**: "Create a hero section"
- **Content writing**: "Write a headline for..."
- **Design advice**: "What colors work for..."
- **Layout suggestions**: "How should I structure..."

---

## Exporting Your Site

### HTML Export

Best for: Static hosting, any web server

```
File → Export HTML → Choose location
```

Output: Single `index.html` with embedded CSS

### React Export

Best for: React applications

```
File → Export React → Choose location
```

Output: `App.js` + component files

### Vue Export

Best for: Vue.js applications

```
File → Export Vue → Choose location
```

Output: `App.vue` SFC

### Deployment

After export:

1. **Static HTML**: Upload to any hosting
2. **React/Vue**: Import into your project
3. **Vercel/Netlify**: Connect Git repo for auto-deploy

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Project |
| Ctrl+Shift+N | New from Template |
| Ctrl+O | Open Project |
| Ctrl+S | Save Project |
| Ctrl+E | Export HTML |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+P | Preview |
| Ctrl+G | Generate with AI |
| Ctrl+, | Settings |
| Delete | Remove selected section |
| ↑/↓ | Move section up/down |

---

## FAQ

### General

**Q: Is WebBuilder free?**
A: Yes, WebBuilder Desktop is free and open-source.

**Q: Do I need internet?**
A: Only for AI features. All other features work offline.

**Q: Where are my projects saved?**
A: `~/.webbuilder/projects/` (usually `C:\Users\You\.webbuilder\projects\`)

**Q: Can I use my own fonts?**
A: Yes, enter any Google Fonts name in the font selector.

### AI Features

**Q: Which AI provider should I use?**
A: OpenAI (GPT-4o) for best results, Anthropic (Claude) for writing, Ollama for free local AI.

**Q: My API key isn't working**
A: Make sure you've restarted WebBuilder after setting the environment variable.

**Q: AI is slow**
A: Response time depends on the model and your internet connection. Try GPT-4o-mini for speed.

### Export

**Q: Can I edit exported code?**
A: Yes! All exported code is clean and readable.

**Q: Why doesn't my exported site look right?**
A: Make sure you're viewing it in a modern browser (Chrome, Firefox, Edge).

**Q: Can I host the exported HTML anywhere?**
A: Yes, it's a single self-contained file.

### Troubleshooting

**Q: App won't start**
A: Make sure you have the latest Windows updates and Visual C++ Redistributable.

**Q: Sections not rendering**
A: Try refreshing the preview (🔄 button) or restarting the app.

**Q: Lost my project**
A: Check `~/.webbuilder/backups/` for automatic backups.

---

## Support

### Getting Help

- **GitHub Issues**: https://github.com/yourusername/webbuilder/issues
- **Email**: support@webbuilder.app
- **Documentation**: https://docs.webbuilder.app

### Reporting Bugs

Please include:
1. WebBuilder version
2. Windows version
3. Steps to reproduce
4. Screenshots if applicable

### Feature Requests

We love hearing ideas! Submit via GitHub Issues with the "enhancement" label.

---

## License

MIT License — Free for personal and commercial use.

---

**Happy building! 🚀**
