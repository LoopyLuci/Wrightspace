# WebBuilder: 100-Year Architecture

## The Core Insight

The greatest web building platform is not the one with the most features. It is the one with the **right foundations** that allow it to evolve for 100 years without becoming obsolete.

**The problem with feature-heavy platforms:**
- They accumulate technical debt
- They become bloated and slow
- They depend on external services that disappear
- They cannot adapt to new paradigms
- They die when the company behind them dies

**The 100-year platform:**
- Has a tiny, perfect core
- Everything else is a plugin
- Uses open, human-readable formats
- Can run offline forever
- Can be maintained by anyone
- Can evolve without breaking

---

## The 7 Principles

### Principle 1: Zero Dependencies in the Core

The core of WebBuilder should depend on **nothing** but the Python standard library.

**Why:**
- External libraries disappear, break, change licenses
- Python stdlib is guaranteed to exist for decades
- Fewer dependencies = fewer failure points
- The core should be able to run on any Python interpreter

**Current state:**
- Core depends on: nothing (good)
- GUI depends on: PyQt5 (acceptable — GUI is replaceable)
- Backend depends on: Flask, etc. (acceptable — backend is optional)

**Rule:**
- `webbuilder/core/` — zero external dependencies
- `webbuilder/gui/` — PyQt5 only (replaceable)
- `webbuilder/agentic/` — Flask only (optional server)
- Everything else is a plugin

### Principle 2: Everything is a Plugin

Every feature beyond the core should be a plugin that can be added, removed, or replaced.

**Why:**
- Features come and go
- Users have different needs
- Plugins can be community-maintained
- The core stays small and stable

**Plugin categories:**
- **Storage plugins** — SQLite, S3, Git, IPFS
- **AI plugins** — OpenAI, Anthropic, Ollama, custom
- **Export plugins** — HTML, React, Vue, Svelte, Angular
- **Theme plugins** — Bootstrap, Tailwind, Bulma, custom
- **Form plugins** — Contact, Survey, Payment, custom
- **Media plugins** — Image, Video, Audio, SVG
- **E-commerce plugins** — Stripe, PayPal, Crypto
- **Publishing plugins** — Vercel, Netlify, Cloudflare, FTP
- **Collaboration plugins** — Git, CRDT, WebSocket
- **Analytics plugins** — Google, Plausible, Matomo

### Principle 3: Open, Human-Readable Native Formats

The native storage format should be open, human-readable, and editable without WebBuilder.

**Why:**
- Users should never be locked in
- Files should be editable with any text editor
- Formats should be documented and stable
- Future tools should be able to read them

**Native formats:**
- **Project** — `.webbuilder/project.json` (JSON)
- **Page** — `.webbuilder/pages/{id}.json` (JSON)
- **Section** — `.webbuilder/sections/{id}.json` (JSON)
- **Asset** — `.webbuilder/assets/{id}.{ext}` (binary)
- **Theme** — `.webbuilder/themes/{id}.json` (JSON)
- **Plugin** — `.webbuilder/plugins/{id}/plugin.json` (JSON)

**All JSON. All human-readable. All editable.**

### Principle 4: Self-Describing System

Every piece of data should describe itself — its type, version, schema, and meaning.

**Why:**
- Future versions can migrate old data
- External tools can understand the data
- No separate schema files that can get lost
- Data is self-documenting

**Example:**
```json
{
  "_schema": "webbuilder/project",
  "_version": "1.0.0",
  "_created": "2026-09-01T00:00:00Z",
  "id": "project-abc123",
  "name": "My Website",
  "pages": [
    {
      "_schema": "webbuilder/page",
      "_version": "1.0.0",
      "id": "page-def456",
      "name": "Home",
      "sections": [
        {
          "_schema": "webbuilder/section",
          "_version": "1.0.0",
          "id": "section-ghi789",
          "type": "Hero",
          "props": {
            "title": "Welcome",
            "subtitle": "Build something amazing"
          }
        }
      ]
    }
  ]
}
```

### Principle 5: Composability Over Monoliths

Small, focused tools that compose together rather than one giant tool.

**Why:**
- Each tool can be understood, tested, and replaced
- Tools can be combined in unexpected ways
- No single point of failure
- Easier to maintain

**The Unix philosophy applied to web building:**
- `webbuilder-create` — create projects
- `webbuilder-add` — add sections
- `webbuilder-export` — export to various formats
- `webbuilder-deploy` — deploy to various platforms
- `webbuilder-serve` — preview locally
- `webbuilder-import` — import from other tools
- `webbuilder-convert` — convert between formats

Each tool does one thing well. They compose via pipes and files.

### Principle 6: Deterministic Behavior

Given the same input, WebBuilder should always produce the same output.

**Why:**
- Reproducible builds
- Testable behavior
- No surprises
- Version control friendly

**Rules:**
- No random IDs (use content hashes)
- No timestamps in output (unless explicitly requested)
- No network calls during build (unless explicitly requested)
- No floating-point calculations that vary by platform
- Sorted keys in all JSON output

### Principle 7: Community Governance

The platform should be governable by its community, not controlled by a single entity.

**Why:**
- Single entities fail, communities endure
- Users should have a say in the platform's direction
- No vendor lock-in
- No single point of failure

**Governance model:**
- **Core** — maintained by community, stable API
- **Plugins** — maintained by anyone, any license
- **Formats** — documented, versioned, backward-compatible
- **Decisions** — RFC process, community voting
- **Funding** — donations, grants, optional paid plugins

---

## The Architecture

### Layer 0: Core (Zero Dependencies)
```
webbuilder/core/
├── __init__.py      # Package init
├── project.py       # Project model (dataclass)
├── page.py          # Page model (dataclass)
├── section.py       # Section model (dataclass)
├── design.py        # Design model (dataclass)
├── storage.py       # Storage interface (abstract)
├── exporter.py      # Export interface (abstract)
├── validator.py     # Validation logic
├── serializer.py    # JSON serialization
└── migrator.py      # Schema migration
```

**Responsibilities:**
- Define data models
- Validate data
- Serialize/deserialize
- Migrate between schema versions

**No external dependencies. No GUI. No network. No AI.**

### Layer 1: Storage Plugins
```
webbuilder/storage/
├── json_files.py    # JSON files on disk (default)
├── sqlite.py        # SQLite database
├── git.py           # Git repository
├── s3.py            # AWS S3
├── ipfs.py          # IPFS distributed storage
└── memory.py        # In-memory (for testing)
```

**Interface:**
```python
class Storage:
    def save_project(self, project: Project) -> None: ...
    def load_project(self, project_id: str) -> Project: ...
    def list_projects(self) -> list[Project]: ...
    def delete_project(self, project_id: str) -> None: ...
```

### Layer 2: Export Plugins
```
webbuilder/export/
├── html.py          # Static HTML (default)
├── react.py         # React components
├── vue.py           # Vue components
├── svelte.py        # Svelte components
├── angular.py       # Angular components
├── json.py          # JSON data
├── markdown.py      # Markdown
├── pdf.py           # PDF output
└── zip.py           # ZIP archive
```

**Interface:**
```python
class Exporter:
    def export(self, project: Project, output_path: Path) -> Path: ...
    def get_name(self) -> str: ...
    def get_file_extension(self) -> str: ...
```

### Layer 3: AI Plugins
```
webbuilder/ai/
├── openai.py        # OpenAI integration
├── anthropic.py     # Anthropic integration
├── ollama.py        # Ollama local models
├── custom.py        # Custom provider
└── none.py          # No AI (default)
```

**Interface:**
```python
class AIProvider:
    def generate(self, prompt: str) -> str: ...
    def stream(self, prompt: str) -> Iterator[str]: ...
    def get_name(self) -> str: ...
    def get_models(self) -> list[str]: ...
```

### Layer 4: GUI (Replaceable)
```
webbuilder/gui/
├── __init__.py      # GUI entry point
├── window.py        # Main window
├── canvas.py        # Visual canvas
├── code_editor.py   # Code editor
├── preview.py       # Preview panel
├── properties.py    # Property inspector
└── ...
```

**Can be replaced with:**
- Web interface (React, Vue, etc.)
- Terminal interface (TUI)
- Headless interface (API only)
- VR interface (future)

### Layer 5: Server (Optional)
```
webbuilder/server/
├── __init__.py      # Server entry point
├── api.py           # REST API
├── websocket.py     # WebSocket
└── cli.py           # CLI interface
```

**Optional. Only needed for:**
- Remote access
- API access
- Collaboration
- CI/CD integration

---

## The Migration Path

### Phase 1: Simplify Core ✅
- Remove all external dependencies from core
- Define clean interfaces for storage, export, AI
- Ensure all data is self-describing

### Phase 2: Extract Plugins
- Move all storage backends to plugins
- Move all export formats to plugins
- Move all AI providers to plugins
- Move all publishing targets to plugins

### Phase 3: Stabilize APIs
- Freeze core API (no breaking changes)
- Document all plugin interfaces
- Create plugin development kit (PDK)

### Phase 4: Build Community
- Create plugin marketplace
- Create documentation site
- Create contribution guidelines
- Create governance model

### Phase 5: Ensure Longevity
- Create format specification
- Create migration tools
- Create compatibility tests
- Create reference implementations

---

## What This Enables

### 10 Years From Now
- WebBuilder runs on Python 40.x
- New AI providers are plugins
- New export formats are plugins
- New storage backends are plugins
- The core is still the same

### 50 Years From Now
- Python is still running
- WebBuilder core is still running
- Plugins have been replaced many times
- The formats are still readable
- The data is still accessible

### 100 Years From Now
- WebBuilder can be reimplemented from the spec
- The formats are still documented
- The data is still readable
- The community still maintains it
- The platform has evolved beyond recognition

---

## The Key Metrics

| Metric | Current | 100-Year Target |
|--------|---------|-----------------|
| Core dependencies | 0 | 0 |
| Core LOC | ~500 | ~500 |
| Plugin interfaces | 5 | 20+ |
| Storage plugins | 1 | 10+ |
| Export plugins | 4 | 50+ |
| AI plugins | 3 | 100+ |
| Lines of documentation | ~1000 | ~50000 |
| Community contributors | 1 | 1000+ |

---

## The Promise

**WebBuilder will outlive its creator.**

Not because it has the most features.
Not because it has the best GUI.
Not because it has the most users.

But because it has the right foundations:
- Zero dependencies in the core
- Everything is a plugin
- Open, human-readable formats
- Self-describing data
- Composable tools
- Deterministic behavior
- Community governance

**This is how you build a platform for 100 years.**
