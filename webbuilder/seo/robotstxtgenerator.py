"""webbuilder.seo.robotstxtgenerator — robots.txt generator."""
from __future__ import annotations
from typing import List, Optional


class RobotsTxtGenerator:
    """Generates robots.txt content."""

    def __init__(self) -> None:
        self._rules: List[str] = []

    def add_rule(self, user_agent: str, allow: Optional[List[str]] = None, disallow: Optional[List[str]] = None) -> None:
        """Add a robots.txt rule."""
        self._rules.append(user_agent)
        if allow:
            for path in allow:
                self._rules.append(f"Allow: {path}")
        if disallow:
            for path in disallow:
                self._rules.append(f"Disallow: {path}")

    def generate(self) -> str:
        """Generate robots.txt content."""
        lines = list(self._rules)
        lines.append("")
        return "\n".join(lines)

    def write(self, output_path: str) -> str:
        """Write robots.txt to a file."""
        content = self.generate()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path