# WebBuilder Documentation
# 100-year survival documentation

## Architecture Overview

WebBuilder is a next-generation agentic web/app building platform designed for century-scale survival.

### Core Principles

1. **Open Standards**: Export to HTML/CSS/JS, React, Vue — formats that outlive any framework
2. **Modularity**: Plugin architecture allows infinite extensibility
3. **Simplicity**: Core is tiny, everything else is a plugin
4. **Backward Compatibility**: Old projects always load, always work
5. **Local-First**: No cloud dependency, your data stays yours

### Project Structure

```
webbuilder/
├── apps/
│   ├── web/           # Web app (Next.js)
│   └── desktop/       # Desktop app (Electron/PyQt)
├── packages/
│   ├── core/          # Core packages
│   │   ├── src/
│   │   │   ├── export/    # Export system
│   │   │   ├── plugins/   # Plugin architecture
│   │   │   ├── neural/    # ML/AI framework
│   │   │   ├── agents/    # Agent chat system
│   │   │   └── api/       # API key management
│   │   └── package.json
│   └── components/    # Component library
├── plugins/           # Community plugins
├── docs/              # Documentation
└── tests/             # Test suite
```

### Plugin API

```python
from webbuilder.plugins import ComponentPlugin

class MyComponent(ComponentPlugin):
    @property
    def name(self) -> str:
        return "my-component"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def render(self, props: Dict) -> str:
        return f"<div>{props.get('title', 'Hello')}</div>"
    
    def get_default_props(self) -> Dict:
        return {'title': 'Hello'}
    
    def get_prop_schema(self) -> Dict:
        return {'title': {'type': 'string', 'label': 'Title'}}
```

### Export Formats

| Format | Description |
|--------|-------------|
| HTML | Static HTML/CSS/JS, works forever |
| React | React components with hooks |
| Vue | Vue 3 Svelte components |
| JSON | Raw project data |

### AI Providers

| Provider | Type | Models |
|----------|------|--------|
| OpenAI | Cloud | GPT-4o, GPT-4, etc. |
| Anthropic | Cloud | Claude 3.5, Claude 3 |
| Google | Cloud | Gemini Pro, Gemini Flash |
| OpenRouter | Cloud | 100+ models |
| Ollama | Local | Llama, Mistral, etc. |
| Custom | Any | Any OpenAI-compatible |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New project |
| Ctrl+O | Open project |
| Ctrl+S | Save project |
| Ctrl+E | Export HTML |
| Ctrl+G | Generate project |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+K | API Key Setup |
| Ctrl+, | Settings |
| Ctrl+Shift+C | Toggle Agent Chat |

### Getting Started

```bash
# Install dependencies
pnpm install

# Start development
pnpm dev

# Run tests
pnpm test

# Build for production
pnpm build
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### License

MIT License - see [LICENSE](LICENSE)
