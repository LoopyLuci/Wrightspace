"""webbuilder.seo.seoanalyzer — SEO analysis engine."""
from __future__ import annotations
from typing import Any, Dict, List

from webbuilder.seo.seometadata import SEOMetadata


class SEOAnalyzer:
    """Analyzes a WebBuilder project or page for SEO compliance."""

    def analyze_page(self, page: Any) -> Dict[str, Any]:
        """Analyze a single page for SEO issues."""
        issues = []
        suggestions = []
        score = 100.0

        title = getattr(page, "title", "") or getattr(page, "name", "")
        if not title:
            issues.append("Page has no title")
            score -= 10
        elif len(title) < 30:
            score -= 5
            suggestions.append("Page title could be longer for better SEO")
        elif len(title) > 60:
            issues.append("Page title is too long")
            score -= 5

        description = getattr(page, "description", "")
        if not description:
            issues.append("Page has no meta description")
            score -= 10
        elif len(description) > 160:
            score -= 5
            suggestions.append("Meta description should be under 160 characters")

        score = max(0, min(100, score))
        return {"score": score, "issues": issues, "suggestions": suggestions, "recommendations": suggestions}

    def analyze(self, html_string: str = "", seo_metadata: SEOMetadata = None) -> Dict[str, Any]:
        """Analyze HTML content and metadata for SEO issues."""
        issues = []
        suggestions = []
        score = 100.0

        if seo_metadata:
            if len(seo_metadata.title) <= 10:
                issues.append("Title is too short")
                score -= 10
            elif len(seo_metadata.title) > 60:
                issues.append("Title is too long")
                score -= 5

            if len(seo_metadata.description) <= 50:
                issues.append("Description is too short")
                score -= 10
            elif len(seo_metadata.description) > 160:
                suggestions.append("Description should be under 160 characters")
                score -= 5

        if html_string:
            if "<title>" not in html_string.lower():
                issues.append("No <title> tag found")
                score -= 10
            if "meta" not in html_string.lower() and "description" not in html_string.lower():
                suggestions.append("Consider adding meta description tag")

        score = max(0, min(100, score))
        return {"score": score, "issues": issues, "suggestions": suggestions, "recommendations": suggestions}
