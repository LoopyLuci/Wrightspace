"""webbuilder.seo.sitemapgenerator — Sitemap XML generator."""
from __future__ import annotations
from pathlib import Path
from typing import Any, List, Optional
from datetime import datetime
from xml.sax.saxutils import escape as xml_escape


class SitemapGenerator:
    """Generates sitemap.xml files from project pages."""

    def __init__(self) -> None:
        self._urls: List[str] = []

    def add_url(self, loc: str, lastmod: str = "", changefreq: str = "weekly", priority: str = "0.8") -> None:
        """Add a URL entry to the sitemap."""
        self._urls.append(loc)

    def generate(self, pages: Optional[List[Any]] = None) -> str:
        """Generate XML sitemap content."""
        urls = []
        if pages:
            for page in pages:
                loc = getattr(page, "url", "") or getattr(page, "path", "")
                if not loc:
                    loc = f"/{getattr(page, 'id', str(id(page)))}"
                loc = xml_escape(loc)
                lastmod = getattr(page, "last_modified", datetime.now().strftime("%Y-%m-%d"))
                if not isinstance(lastmod, str):
                    lastmod = lastmod.strftime("%Y-%m-%d")
                urls.append(
                    "    <url>\n"
                    f"      <loc>{loc}</loc>\n"
                    f"      <lastmod>{lastmod}</lastmod>\n"
                    "      <changefreq>weekly</changefreq>\n"
                    "      <priority>0.8</priority>\n"
                    "    </url>"
                )
        else:
            for url in self._urls:
                urls.append(
                    "    <url>\n"
                    f"      <loc>{xml_escape(url)}</loc>\n"
                    "      <changefreq>weekly</changefreq>\n"
                    "      <priority>0.8</priority>\n"
                    "    </url>"
                )
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]
        lines.extend(urls)
        lines.append("</urlset>")
        return "\n".join(lines)

    def save(self, path: Path) -> None:
        """Write sitemap.xml to a file."""
        content = self.generate()
        Path(path).write_text(content, encoding="utf-8")