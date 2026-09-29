"""webbuilder.seo — auto-generated implementation."""

from __future__ import annotations

class RobotsTxtGenerator:
    """RobotsTxtGenerator."""

    def __init__(self):

        self.rules = []

    def add_rule(self, user_agent, allow=None, disallow=None):

        rule = {'user_agent': user_agent, 'allow': allow or [], 'disallow': disallow or []}

        self.rules.append(rule)

    def generate(self):

        lines = []

        for rule in self.rules:

            lines.append(rule['user_agent'])

            for a in rule['allow']:

                lines.append(f'Allow: {a}')

            for d in rule['disallow']:

                lines.append(f'Disallow: {d}')

            lines.append('')

        return '\n'.join(lines)

    pass

class SEOAnalyzer:
    """SEOAnalyzer."""

    def __init__(self):

        pass

    def analyze(self, html_content, metadata=None):

        result = {'score': 100, 'issues': [], 'warnings': [], 'recommendations': []}

        if metadata:

            if not metadata.title:

                result['score'] -= 20

                result['issues'].append('Missing title tag')

            if not metadata.description:

                result['score'] -= 15

                result['issues'].append('Missing meta description')

        return result

    pass

class SEOMetadata:
    """SEOMetadata."""

    def __init__(self, title='', description='', keywords='', author='', og_image=None, canonical_url=None, no_index=False, no_follow=False, structured_data=None):

        self.title = title

        self.description = description

        self.keywords = keywords

        self.author = author

        self.og_image = og_image

        self.canonical_url = canonical_url

        self.no_index = no_index

        self.no_follow = no_follow

        self.structured_data = structured_data or {}

    def to_meta_tags(self):

        tags = []

        if self.title:

            tags.append(f'<title>{self.title}</title>')

        if self.description:

            tags.append(f'<meta name="description" content="{self.description}">')

        return '\n'.join(tags)

    def to_structured_data(self):

        import json

        return json.dumps(self.structured_data, indent=2)

    def validate(self):

        errors = []

        if not self.title or len(self.title) < 10:

            errors.append('Title is too short (min 10 chars)')

        if not self.description or len(self.description) < 50:

            errors.append('Description is too short (min 50 chars)')

        if len(self.title) > 70:

            errors.append('Title is too long (max 70 chars)')

        return errors

    pass

class SitemapGenerator:
    """SitemapGenerator."""

    def __init__(self, base_url='http://localhost'):

        self.base_url = base_url

        self.pages = []

    def add_page(self, url, lastmod=None, changefreq='weekly', priority='0.5'):

        self.pages.append({'url': url, 'lastmod': lastmod, 'changefreq': changefreq, 'priority': priority})

    def generate(self):

        lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

        for page in self.pages:

            lines.append('  <url>')

            lines.append(f'    <loc>{self.base_url}{page["url"]}</loc>')

            if page['lastmod']:

                lines.append(f'    <lastmod>{page["lastmod"]}</lastmod>')

            lines.append(f'    <changefreq>{page["changefreq"]}</changefreq>')

            lines.append(f'    <priority>{page["priority"]}</priority>')

            lines.append('  </url>')

        lines.append('</urlset>')

        return '\n'.join(lines)

    def save(self, path):

        path.write_text(self.generate())

    pass


__all__ = ['RobotsTxtGenerator', 'SEOAnalyzer', 'SEOMetadata', 'SitemapGenerator']
