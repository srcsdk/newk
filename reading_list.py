#!/usr/bin/env python3
"""reading list export to markdown and html formats"""

import json
import os
from datetime import datetime


READING_LIST_FILE = os.path.join(os.path.dirname(__file__), "reading_list.json")


def load_reading_list():
    """load saved reading list."""
    if os.path.exists(READING_LIST_FILE):
        with open(READING_LIST_FILE, "r") as f:
            return json.load(f)
    return []


def save_reading_list(items):
    """save reading list."""
    with open(READING_LIST_FILE, "w") as f:
        json.dump(items, f, indent=2)


def add_to_list(title, url, category="uncategorized", notes=""):
    """add article to reading list."""
    items = load_reading_list()
    items.append({
        "title": title,
        "url": url,
        "category": category,
        "notes": notes,
        "added": datetime.now().isoformat(),
        "read": False,
    })
    save_reading_list(items)


def export_markdown(items=None):
    """export reading list as markdown."""
    if items is None:
        items = load_reading_list()
    by_category = {}
    for item in items:
        cat = item.get("category", "uncategorized")
        by_category.setdefault(cat, []).append(item)
    lines = ["# reading list", ""]
    for category in sorted(by_category.keys()):
        lines.append(f"## {category}")
        lines.append("")
        for item in by_category[category]:
            status = "x" if item.get("read") else " "
            lines.append(f"- [{status}] [{item['title']}]({item['url']})")
            if item.get("notes"):
                lines.append(f"  - {item['notes']}")
        lines.append("")
    return "\n".join(lines)


def export_html(items=None):
    """export reading list as html."""
    if items is None:
        items = load_reading_list()
    by_category = {}
    for item in items:
        cat = item.get("category", "uncategorized")
        by_category.setdefault(cat, []).append(item)
    parts = ["<html><head><title>reading list</title></head><body>"]
    parts.append("<h1>reading list</h1>")
    for category in sorted(by_category.keys()):
        parts.append(f"<h2>{category}</h2><ul>")
        for item in by_category[category]:
            parts.append(f'<li><a href="{item["url"]}">{item["title"]}</a></li>')
        parts.append("</ul>")
    parts.append("</body></html>")
    return "\n".join(parts)


if __name__ == "__main__":
    items = load_reading_list()
    print(f"reading list: {len(items)} items")
    md = export_markdown(items)
    print(md[:500] if md else "empty")
