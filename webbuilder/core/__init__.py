"""webbuilder.core — Core project data models and storage."""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import html
import json
import os
import re
import tempfile
import uuid
from datetime import datetime


@dataclass
class Design:
    """Design settings for a project."""
    colors: dict[str, str] = field(default_factory=lambda: {
        "primary": "#3b82f6",
        "secondary": "#1e293b",
        "accent": "#8b5cf6",
        "background": "#0a0a0f",
        "text": "#e2e8f0",
        "heading": "#f8fafc",
    })
    fonts: dict[str, str] = field(default_factory=lambda: {
        "heading": "Inter",
        "body": "Inter",
        "mono": "JetBrains Mono",
    })
    max_width: int = 1200
    border_radius: int = 8
    shadow: str = "0 4px 6px rgba(0,0,0,0.3)"

    def to_dict(self) -> dict:
        return {
            "_schema": "webbuilder/design",
            "_version": "1.0",
            "colors": self.colors,
            "fonts": self.fonts,
            "max_width": self.max_width,
            "border_radius": self.border_radius,
            "shadow": self.shadow,
        }


@dataclass
class Section:
    """A content section in a page."""
    id: str
    type: str
    props: dict[str, Any] = field(default_factory=dict)
    order: int = 0

    def to_dict(self) -> dict:
        return {
            "_schema": "webbuilder/section",
            "_version": "1.0",
            "id": self.id,
            "type": self.type,
            "props": self.props,
            "order": self.order,
        }


@dataclass
class Page:
    """A page in a project."""
    id: str
    name: str
    sections: list[Section] = field(default_factory=list)
    title: str = ""
    description: str = ""

    def add_section(self, section_type: str, props: dict[str, Any] | None = None) -> Section:
        """Add a section to this page."""
        section = Section(
            id=f"sec-{len(self.sections)}-{uuid.uuid4().hex[:8]}",
            type=section_type,
            props=props or {},
            order=len(self.sections),
        )
        self.sections.append(section)
        return section

    def to_dict(self) -> dict:
        return {
            "_schema": "webbuilder/page",
            "_version": "1.0",
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "sections": [s.to_dict() for s in self.sections],
        }


@dataclass
class Project:
    """A WebBuilder project."""
    id: str
    name: str
    description: str = ""
    pages: list[Page] = field(default_factory=list)
    design: Design = field(default_factory=Design)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: list[str] = field(default_factory=list)
    settings: dict[str, Any] = field(default_factory=dict)

    def add_page(self, name: str) -> Page:
        """Add a page to this project."""
        page = Page(id=f"page-{len(self.pages)}-{uuid.uuid4().hex[:8]}", name=name)
        self.pages.append(page)
        return page

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "_schema": "webbuilder/project",
            "_version": "1.0",
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "pages": [p.to_dict() for p in self.pages],
            "design": self.design.to_dict(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tags": self.tags,
            "settings": self.settings,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Project:
        """Deserialize from dictionary."""
        design_data = data.get("design", {})
        design = Design(
            colors=design_data.get("colors", {}),
            fonts=design_data.get("fonts", {}),
            max_width=design_data.get("max_width", 1200),
            border_radius=design_data.get("border_radius", 8),
            shadow=design_data.get("shadow", "0 4px 6px rgba(0,0,0,0.3)"),
        )
        project = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Untitled"),
            description=data.get("description", ""),
            pages=[],
            design=design,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            tags=data.get("tags", []),
            settings=data.get("settings", {}),
        )
        for p_data in data.get("pages", []):
            page = Page(
                id=p_data.get("id", str(uuid.uuid4())),
                name=p_data.get("name", "Untitled"),
                title=p_data.get("title", ""),
                description=p_data.get("description", ""),
            )
            for s_data in p_data.get("sections", []):
                page.sections.append(Section(
                    id=s_data.get("id", str(uuid.uuid4())),
                    type=s_data.get("type", ""),
                    props=s_data.get("props", {}),
                    order=s_data.get("order", 0),
                ))
            project.pages.append(page)
        return project


class ProjectManager:
    """Manages project persistence."""

    def __init__(self, storage_dir: Path | None = None):
        self.storage_dir = storage_dir or Path.home() / ".webbuilder" / "projects"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _project_path(self, project_id: str) -> Path:
        return self.storage_dir / f"{project_id}.json"

    def create_new(self, name: str) -> Project:
        """Create a new project."""
        project = Project(
            id=f"project-{uuid.uuid4().hex[:12]}",
            name=name,
        )
        project.pages.append(Page(id=f"page-0-{uuid.uuid4().hex[:8]}", name="Home"))
        self.save(project)
        return project

    def save(self, project: Project) -> Path:
        """Save a project to disk with atomic write."""
        project.updated_at = datetime.now().isoformat()
        path = self._project_path(project.id)
        tmp_fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix='.tmp')
        try:
            with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, indent=2)
            os.replace(tmp_path, path)
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
        return path

    def load(self, project_id: str) -> Project | None:
        """Load a project from disk."""
        path = self._project_path(project_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding='utf-8'))
        return Project.from_dict(data)

    def list_projects(self) -> list[dict]:
        """List all projects."""
        projects = []
        for path in self.storage_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
                projects.append({
                    "id": data.get("id", ""),
                    "name": data.get("name", ""),
                    "updated_at": data.get("updated_at", ""),
                })
            except (json.JSONDecodeError, OSError):
                continue
        return sorted(projects, key=lambda p: p.get("updated_at", ""), reverse=True)

    def delete(self, project_id: str) -> bool:
        """Delete a project."""
        path = self._project_path(project_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def backup(self, project_id: str) -> Path:
        """Create a backup of a project with atomic write."""
        project = self.load(project_id)
        if project is None:
            raise ValueError(f"Project {project_id} not found")
        backup_dir = self.storage_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = backup_dir / f"{project_id}-{timestamp}.json"
        tmp_fd, tmp_path = tempfile.mkstemp(dir=backup_dir, suffix='.tmp')
        try:
            with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, indent=2)
            os.replace(tmp_path, path)
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
        return path


# ── Color validation ─────────────────────────────────────────────────────────

NAMED_COLORS = frozenset({
    "aliceblue", "antiquewhite", "aqua", "aquamarine", "azure",
    "beige", "bisque", "black", "blanchedalmond", "blue",
    "blueviolet", "brown", "burlywood", "cadetblue", "chartreuse",
    "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson",
    "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray",
    "darkgreen", "darkkhaki", "darkmagenta", "darkolivegreen",
    "darkorange", "darkorchid", "darkred", "darksalmon",
    "darkseagreen", "darkslateblue", "darkslategray", "darkturquoise",
    "darkviolet", "deeppink", "deepskyblue", "dimgray", "dodgerblue",
    "firebrick", "floralwhite", "forestgreen", "fuchsia", "gainsboro",
    "ghostwhite", "gold", "goldenrod", "gray", "green", "greenyellow",
    "honeydew", "hotpink", "indianred", "indigo", "ivory", "khaki",
    "lavender", "lavenderblush", "lawngreen", "lemonchiffon",
    "lightblue", "lightcoral", "lightcyan", "lightgoldenrodyellow",
    "lightgreen", "lightgrey", "lightpink", "lightsalmon",
    "lightseagreen", "lightskyblue", "lightslategray", "lightsteelblue",
    "lightyellow", "lime", "limegreen", "linen", "magenta", "maroon",
    "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple",
    "mediumseagreen", "mediumslateblue", "mediumspringgreen",
    "mediumturquoise", "mediumvioletred", "midnightblue", "mintcream",
    "mistyrose", "moccasin", "navajowhite", "navy", "oldlace", "olive",
    "olivedrab", "orange", "orangered", "orchid", "palegoldenrod",
    "palegreen", "paleturquoise", "palevioletred", "papayawhip",
    "peachpuff", "peru", "pink", "plum", "powderblue", "purple",
    "rebeccapurple", "red", "rosybrown", "royalblue", "saddlebrown",
    "salmon", "sandybrown", "seagreen", "seashell", "sienna", "silver",
    "skyblue", "slateblue", "slategray", "snow", "springgreen",
    "steelblue", "tan", "teal", "thistle", "tomato", "transparent",
    "turquoise", "violet", "wheat", "white", "whitesmoke", "yellow",
    "yellowgreen",
})

_HEX_RE = re.compile(r'^#([0-9a-f]{3}|[0-9a-f]{4}|[0-9a-f]{6}|[0-9a-f]{8})$')
_RGB_RE = re.compile(r'^rgba?\s*\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*([\d.]+)\s*)?\)$')
_HSL_RE = re.compile(r'^hsla?\s*\(\s*(\d{1,3})\s*,\s*(\d{1,3})%?\s*,\s*(\d{1,3})%?\s*(?:,\s*([\d.]+)\s*)?\)$')


def _is_valid_color(value: str) -> bool:
    """Check if a value is a valid CSS color."""
    if not isinstance(value, str) or not value:
        return False
    value = value.strip().lower()
    if value in NAMED_COLORS or value in ("inherit", "transparent"):
        return True
    if _HEX_RE.match(value):
        return True
    m = _RGB_RE.match(value)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
            if m.group(4) is None:
                return True
            try:
                return 0.0 <= float(m.group(4)) <= 1.0
            except ValueError:
                return False
    m = _HSL_RE.match(value)
    if m:
        h, s, l = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100:
            if m.group(4) is None:
                return True
            try:
                return 0.0 <= float(m.group(4)) <= 1.0
            except ValueError:
                return False
    return False


def is_valid_color(value: str) -> bool:
    """Check if a value is a valid CSS color."""
    return _is_valid_color(value)


# ── Sanitization ─────────────────────────────────────────────────────────────

def sanitize(value: str) -> str:
    """Sanitize a string for safe display."""
    return sanitize_string(value)


def sanitize_string(value: str, max_length: int = 10000) -> str:
    """Sanitize a string input, escaping HTML tags and removing null bytes."""
    if not isinstance(value, str):
        return ""
    value = value.replace('\x00', '').strip()
    value = html.escape(value)
    if len(value) > max_length:
        value = value[:max_length]
    return value


def sanitize_url(url: str):
    """Sanitize a URL. Returns the safe URL string, or False if blocked."""
    if not isinstance(url, str):
        return False
    url = url.strip()
    if url.lower().startswith(('javascript:', 'data:', 'vbscript:')):
        return False
    if url.startswith(('http://', 'https://', '/', '#?')):
        return url
    return False


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename."""
    if not filename or not isinstance(filename, str):
        return "unnamed"
    filename = filename.replace('\x00', '')
    filename = filename.replace('..', '')
    filename = filename.replace('/', '_').replace('\\', '_')
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename).strip()
    if len(filename) > 255:
        filename = filename[:255]
    if not filename:
        filename = "unnamed"
    return filename


# ── Section type validation ──────────────────────────────────────────────────

VALID_SECTION_TYPES = [
    "Navbar", "Hero — Centered", "Hero — Split", "Hero — Fullscreen",
    "Features — 3 Columns", "Features — Grid", "Features — List",
    "Pricing — 3 Tiers", "Pricing — Table",
    "CTA — Centered", "CTA — Split",
    "Stats — Numbers", "Stats — Grid",
    "Testimonials — Carousel", "Testimonials — Grid",
    "FAQ — Accordion", "FAQ — List",
    "Footer", "Contact — Form", "Contact — Info",
    "Blog — Grid", "Blog — List",
    "Team — Grid", "Team — Cards",
    "Portfolio — Grid", "Portfolio — Masonry",
    "Clients — Logos", "Clients — Testimonials",
    "Steps — Numbered", "Steps — Timeline",
    "Comparison — Table", "Comparison — Side by Side",
    "Gallery — Grid", "Gallery — Masonry",
    "Values — Icons", "Values — Text",
    "Newsletter — Centered", "Newsletter — Split",
    "Pricing — Toggle", "FAQ — Toggle",
]


def validate_section_type(section_type: str) -> str | None:
    """Validate a section type name. Returns error message or None."""
    if not section_type or not isinstance(section_type, str):
        return "Section type must be a non-empty string"
    normalized = section_type.strip()
    if not normalized:
        return "Section type must be a non-empty string"
    for valid in VALID_SECTION_TYPES:
        if normalized.lower() == valid.lower():
            return None
    return f"Unknown section type: '{section_type}'. Valid types: {', '.join(VALID_SECTION_TYPES[:10])}..."


def validate_section_props(section_type: str, props: dict) -> list[str]:
    """Validate section props for a given section type."""
    errors = []
    if not isinstance(props, dict):
        return ["Section props must be a dictionary"]
    t = section_type.lower()
    if "hero" in t:
        if "title" in props and not isinstance(props["title"], str):
            errors.append("Hero title must be a string")
        if "subtitle" in props and not isinstance(props["subtitle"], str):
            errors.append("Hero subtitle must be a string")
        if "ctaText" in props and not isinstance(props["ctaText"], str):
            errors.append("Hero CTA text must be a string")
        if "backgroundColor" in props and props["backgroundColor"] and not _is_valid_color(props["backgroundColor"]):
            errors.append("Hero backgroundColor must be a valid CSS color")
    if "features" in t:
        if "title" in props and not isinstance(props["title"], str):
            errors.append("Features title must be a string")
        if "items" in props:
            if not isinstance(props["items"], list):
                errors.append("Features items must be a list")
            else:
                for i, item in enumerate(props["items"]):
                    if not isinstance(item, dict):
                        errors.append(f"Features item {i} must be a dictionary")
                    elif "title" not in item:
                        errors.append(f"Features item {i} missing title")
                    elif "description" not in item:
                        errors.append(f"Features item {i} missing description")
    if "pricing" in t:
        if "title" in props and not isinstance(props["title"], str):
            errors.append("Pricing title must be a string")
        if "tiers" in props:
            if not isinstance(props["tiers"], list):
                errors.append("Pricing tiers must be a list")
            elif len(props["tiers"]) < 2:
                errors.append("Pricing needs at least 2 tiers")
            else:
                for i, tier in enumerate(props["tiers"]):
                    if not isinstance(tier, dict):
                        errors.append(f"Pricing tier {i} must be a dictionary")
                    elif "name" not in tier:
                        errors.append(f"Pricing tier {i} missing name")
                    elif "price" not in tier:
                        errors.append(f"Pricing tier {i} missing price")
    if "cta" in t:
        if "title" in props and not isinstance(props["title"], str):
            errors.append("CTA title must be a string")
        if "buttonText" in props and not isinstance(props["buttonText"], str):
            errors.append("CTA button text must be a string")
        if "backgroundColor" in props and props["backgroundColor"] and not _is_valid_color(props["backgroundColor"]):
            errors.append("CTA backgroundColor must be a valid CSS color")
    if "stats" in t:
        if "title" in props and not isinstance(props["title"], str):
            errors.append("Stats title must be a string")
        if "items" in props:
            if not isinstance(props["items"], list):
                errors.append("Stats items must be a list")
            else:
                for i, item in enumerate(props["items"]):
                    if not isinstance(item, dict):
                        errors.append(f"Stats item {i} must be a dictionary")
                    elif "value" not in item:
                        errors.append(f"Stats item {i} missing value")
                    elif "label" not in item:
                        errors.append(f"Stats item {i} missing label")
    if "testimonials" in t:
        if "title" in props and not isinstance(props["title"], str):
            errors.append("Testimonials title must be a string")
        if "items" in props:
            if not isinstance(props["items"], list):
                errors.append("Testimonials items must be a list")
            else:
                for i, item in enumerate(props["items"]):
                    if not isinstance(item, dict):
                        errors.append(f"Testimonial {i} must be a dictionary")
                    elif "quote" not in item:
                        errors.append(f"Testimonial {i} missing quote")
                    elif "author" not in item:
                        errors.append(f"Testimonial {i} missing author")
    if "faq" in t:
        if "title" in props and not isinstance(props["title"], str):
            errors.append("FAQ title must be a string")
        if "items" in props:
            if not isinstance(props["items"], list):
                errors.append("FAQ items must be a list")
            else:
                for i, item in enumerate(props["items"]):
                    if not isinstance(item, dict):
                        errors.append(f"FAQ item {i} must be a dictionary")
                    elif "question" not in item:
                        errors.append(f"FAQ item {i} missing question")
                    elif "answer" not in item:
                        errors.append(f"FAQ item {i} missing answer")
    if "footer" in t:
        if "copyright" in props and not isinstance(props["copyright"], str):
            errors.append("Footer copyright must be a string")
    return errors


# ── Project validation ───────────────────────────────────────────────────────

def validate_project(project: Any) -> list[str]:
    """Validate a project (dict or Project instance), returning a list of errors."""
    if isinstance(project, Project):
        project = project.to_dict()
    errors = []
    if not isinstance(project, dict):
        return ["Project must be a dictionary"]
    if "id" not in project:
        errors.append("Missing required field: id")
    elif not isinstance(project["id"], str) or not re.match(r'^[a-zA-Z0-9_-]+$', project["id"]):
        errors.append(f"Invalid project ID: {project.get('id')}")
    if "name" not in project:
        errors.append("Missing required field: name")
    elif not isinstance(project["name"], str) or len(project["name"].strip()) == 0:
        errors.append("Project name must be a non-empty string")
    elif len(project["name"]) > 100:
        errors.append("Project name too long (max 100 characters)")
    if "pages" not in project:
        errors.append("Missing required field: pages")
    elif not isinstance(project["pages"], list):
        errors.append("pages must be a list")
    else:
        for i, page in enumerate(project["pages"]):
            if not isinstance(page, dict):
                errors.append(f"Page {i} must be a dictionary")
                continue
            if "id" not in page:
                errors.append(f"Page {i} missing id")
            if "name" not in page:
                errors.append(f"Page {i} missing name")
            if "sections" in page and not isinstance(page["sections"], list):
                errors.append(f"Page {i} sections must be a list")
    if "pages" in project and isinstance(project["pages"], list) and len(project["pages"]) == 0:
        errors.append("Project must have at least one page")
    if "design" in project:
        design = project["design"]
        if isinstance(design, dict) and "colors" in design:
            colors = design["colors"]
            if isinstance(colors, dict):
                for name, value in colors.items():
                    if not isinstance(value, str):
                        errors.append(f"Color '{name}' must be a string")
                    elif value and not _is_valid_color(value):
                        errors.append(f"Invalid color value for '{name}': {value}")
    return errors


# ── InputValidator (static utilities) ────────────────────────────────────────

class InputValidator:
    """Input validation utilities."""

    @staticmethod
    def validate_project_name(name: str) -> tuple[bool, str | None]:
        if not name or not isinstance(name, str):
            return False, "Project name is required"
        name = name.strip()
        if len(name) == 0:
            return False, "Project name cannot be empty"
        if len(name) > 100:
            return False, "Project name too long (max 100 characters)"
        if re.search(r'[<>:"/\\|?*]', name):
            return False, "Project name contains invalid characters"
        return True, None

    @staticmethod
    def validate_section_type(section_type: str) -> tuple[bool, str | None]:
        error = validate_section_type(section_type)
        if error:
            return False, error
        return True, None

    @staticmethod
    def validate_section_props(section_type: str, props: dict) -> tuple[bool, list[str]]:
        errors = validate_section_props(section_type, props)
        return len(errors) == 0, errors

    @staticmethod
    def validate_api_key(provider_id: str, api_key: str) -> tuple[bool, str | None]:
        if not api_key or not isinstance(api_key, str):
            return False, "API key is required"
        if provider_id == "openai":
            if not api_key.startswith("sk-"):
                return False, "OpenAI API key must start with 'sk-'"
            if len(api_key) < 20:
                return False, "OpenAI API key appears invalid (too short)"
        elif provider_id == "anthropic":
            if not api_key.startswith("sk-ant-"):
                return False, "Anthropic API key must start with 'sk-ant-'"
        elif provider_id == "google":
            if not api_key.startswith("AIza"):
                return False, "Google API key must start with 'AIza'"
        return True, None

    @staticmethod
    def validate_file_path(path: str) -> tuple[bool, str | None]:
        if not path or ".." in path:
            return False, "Path traversal not allowed"
        if path.startswith("/etc/") or path.startswith("/proc/"):
            return False, "System paths not allowed"
        return True, None

    @staticmethod
    def sanitize_string(value: str, max_length: int = 10000) -> str:
        return sanitize_string(value, max_length)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        return sanitize_filename(filename)

    @staticmethod
    def sanitize_url(url: str) -> str:
        return sanitize_url(url)


__all__ = [
    "Design", "Page", "Section", "Project", "ProjectManager",
    "validate_project", "validate_section_type", "validate_section_props",
    "is_valid_color", "sanitize", "sanitize_string", "sanitize_url",
    "sanitize_filename", "InputValidator", "NAMED_COLORS", "VALID_SECTION_TYPES",
    "MultiPageProject", "AssetManager", "DeploymentManager",
]

# Lazy re-exports from submodules for convenience
def __getattr__(name: str):
    if name == "MultiPageProject":
        from webbuilder.core.multi.multipageproject import MultiPageProject
        return MultiPageProject
    if name == "AssetManager":
        from webbuilder.core.multi.assetmanager import AssetManager
        return AssetManager
    if name == "DeploymentManager":
        from webbuilder.core.multi.deploymentmanager import DeploymentManager
        return DeploymentManager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
