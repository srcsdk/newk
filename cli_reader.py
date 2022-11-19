#!/usr/bin/env python3
"""terminal-based article reader"""

import textwrap
import re


def render_article(article, width=80):
    """render article content for terminal display."""
    lines = []
    title = article.get("title", "untitled")
    lines.append("=" * width)
    for line in textwrap.wrap(title, width):
        lines.append(line)
    lines.append("=" * width)
    meta_parts = []
    if article.get("author"):
        meta_parts.append(f"by {article['author']}")
    if article.get("source"):
        meta_parts.append(article["source"])
    if article.get("date"):
        meta_parts.append(article["date"])
    if meta_parts:
        lines.append(" | ".join(meta_parts))
    lines.append("-" * width)
    content = article.get("content", article.get("description", ""))
    content = _strip_html(content)
    paragraphs = content.split("\n\n")
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        wrapped = textwrap.wrap(para, width)
        lines.extend(wrapped)
        lines.append("")
    if article.get("url"):
        lines.append(f"link: {article['url']}")
    if article.get("categories"):
        lines.append(f"tags: {', '.join(article['categories'])}")
    lines.append("-" * width)
    return "\n".join(lines)


def _strip_html(text):
    """remove html tags from text."""
    import html as html_mod
    text = html_mod.unescape(text)
    text = re.sub(r'<br\s*/?>\s*', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<p[^>]*>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def render_article_list(articles, width=80):
    """render list of articles for terminal."""
    lines = []
    for i, article in enumerate(articles, 1):
        title = article.get("title", "untitled")
        source = article.get("source", "")
        date = article.get("date", "")[:10]
        prefix = f"{i:3d}. "
        max_title = width - len(prefix) - len(source) - len(date) - 4
        if len(title) > max_title:
            title = title[:max_title - 3] + "..."
        line = f"{prefix}{title}"
        right = f"  {source} {date}".rstrip()
        pad = width - len(line) - len(right)
        if pad < 1:
            pad = 1
        lines.append(line + " " * pad + right)
    return "\n".join(lines)


if __name__ == "__main__":
    article = {
        "title": "python 3.11 released with major performance improvements",
        "author": "python team",
        "source": "python.org",
        "date": "2022-10-24",
        "description": "python 3.11 brings significant speed improvements. "
                       "the new version is up to 25% faster than python 3.10.",
        "url": "https://python.org/downloads/",
        "categories": ["python", "release"],
    }
    print(render_article(article, 70))
