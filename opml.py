#!/usr/bin/env python3
"""opml import and export for feed subscriptions"""

import re


def parse_opml(content):
    """parse opml xml content into list of feed dicts."""
    feeds = []
    outlines = re.findall(r'<outline[^/]*/>', content)
    for outline in outlines:
        title = _attr(outline, "title") or _attr(outline, "text")
        url = _attr(outline, "xmlUrl")
        html_url = _attr(outline, "htmlUrl")
        category = _attr(outline, "category") or "uncategorized"
        if url:
            feeds.append({
                "title": title or url,
                "url": url,
                "html_url": html_url or "",
                "category": category,
            })
    return feeds


def _attr(tag, name):
    """extract attribute value from xml tag string."""
    match = re.search(rf'{name}="([^"]*)"', tag)
    return match.group(1) if match else ""


def generate_opml(feeds, title="feed subscriptions"):
    """generate opml xml from list of feed dicts."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<opml version="2.0">',
        '  <head>',
        f'    <title>{title}</title>',
        '  </head>',
        '  <body>',
    ]
    by_category = {}
    for feed in feeds:
        cat = feed.get("category", "uncategorized")
        by_category.setdefault(cat, []).append(feed)
    for cat, cat_feeds in sorted(by_category.items()):
        lines.append(f'    <outline text="{cat}">')
        for f in cat_feeds:
            lines.append(
                f'      <outline text="{f["title"]}" '
                f'xmlUrl="{f["url"]}" '
                f'htmlUrl="{f.get("html_url", "")}" />'
            )
        lines.append('    </outline>')
    lines.append('  </body>')
    lines.append('</opml>')
    return "\n".join(lines)


def merge_feeds(existing, imported):
    """merge imported feeds with existing, avoiding duplicates by url."""
    urls = {f["url"] for f in existing}
    merged = list(existing)
    added = 0
    for feed in imported:
        if feed["url"] not in urls:
            merged.append(feed)
            urls.add(feed["url"])
            added += 1
    return merged, added


if __name__ == "__main__":
    feeds = [
        {"title": "test feed", "url": "https://example.com/feed.xml",
         "category": "tech"},
    ]
    opml = generate_opml(feeds)
    print(opml[:200])
    parsed = parse_opml(opml)
    print(f"parsed {len(parsed)} feeds")
