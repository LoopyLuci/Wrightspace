"""webbuilder.seo.seometadata — SEO metadata container."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json


@dataclass
class SEOMetadata:
    """SEO metadata for a page or project."""
    title: str = ""
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    author: str = ""
    canonical_url: str = ""
    robots: str = "index, follow"
    structured_data: Dict[str, Any] = field(default_factory=dict)
    social: Dict[str, str] = field(default_factory=dict)

    def to_meta_tags(self) -> str:
        """Generate HTML meta tags string."""
        tags = [f"<title>{self.title}</title>"]
        tags.append(f'<meta name="description" content="{self.description}">')
        if self.keywords:
            tags.append(f'<meta name="keywords" content="{", ".join(self.keywords)}">')
        if self.author:
            tags.append(f'<meta name="author" content="{self.author}">')
        if self.canonical_url:
            tags.append(f'<link rel="canonical" href="{self.canonical_url}">')
        tags.append(f'<meta name="robots" content="{self.robots}">')
        return "\n".join(tags)

    def to_structured_data(self) -> str:
        """Generate JSON-LD structured data string."""
        return json.dumps(self.structured_data, indent=2)

    def validate(self) -> List[str]:
        """Validate SEO metadata and return list of errors."""
        errors = []
        if len(self.title) <= 10:
            errors.append("Title must be longer than 10 characters")
        if len(self.description) <= 50:
            errors.append("Description must be longer than 50 characters")
        return errors

    def to_dict(self) -> Dict[str, object]:
        """Serialize to a dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "author": self.author,
            "canonical_url": self.canonical_url,
            "robots": self.robots,
            "structured_data": self.structured_data,
            "social": self.social,
        }
