#!/usr/bin/env python3
"""export feeds to json and opml formats"""

import json
import time
import xml.etree.ElementTree as ET


def export_feeds_json(feeds, filepath):
    """export feed list to json format"""
    data = {
        "exported": time.strftime("%Y-%m-%d %H:%M:%S"),
        "feeds": [],
    }
    for feed in feeds:
        if isinstance(feed, str):
            data["feeds"].append({"url": feed})
        elif isinstance(feed, dict):
            data["feeds"].append(feed)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    return len(data["feeds"])


def export_opml(feeds, filepath, title="newk feeds"):
    """export feed list to opml format for import in other readers"""
    root = ET.Element("opml", version="2.0")
    head = ET.SubElement(root, "head")
    ET.SubElement(head, "title").text = title
    ET.SubElement(head, "dateCreated").text = time.strftime(
        "%a, %d %b %Y %H:%M:%S %z")

    body = ET.SubElement(root, "body")

    # group by category if available
    categories = {}
    uncategorized = []
    for feed in feeds:
        if isinstance(feed, str):
            uncategorized.append({"url": feed, "title": feed})
        elif isinstance(feed, dict):
            cat = feed.get("category", "")
            if cat:
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(feed)
            else:
                uncategorized.append(feed)

    for cat, cat_feeds in sorted(categories.items()):
        outline = ET.SubElement(body, "outline", text=cat, title=cat)
        for feed in cat_feeds:
            ET.SubElement(outline, "outline",
                          type="rss",
                          text=feed.get("title", feed.get("url", "")),
                          xmlUrl=feed.get("url", ""),
                          htmlUrl=feed.get("site_url", ""))

    for feed in uncategorized:
        ET.SubElement(body, "outline",
                      type="rss",
                      text=feed.get("title", feed.get("url", "")),
                      xmlUrl=feed.get("url", ""),
                      htmlUrl=feed.get("site_url", ""))

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(filepath, encoding="utf-8", xml_declaration=True)
    return len(feeds)


def import_opml(filepath):
    """import feeds from an opml file"""
    tree = ET.parse(filepath)
    root = tree.getroot()
    feeds = []

    for outline in root.iter("outline"):
        xml_url = outline.get("xmlUrl", "")
        if xml_url:
            feed = {
                "url": xml_url,
                "title": outline.get("text", outline.get("title", "")),
                "site_url": outline.get("htmlUrl", ""),
            }
            # check if inside a category outline
            parent = None
            for parent_el in root.iter():
                if outline in list(parent_el):
                    parent = parent_el
                    break
            if parent is not None and parent.tag == "outline":
                feed["category"] = parent.get("text", "")
            feeds.append(feed)

    return feeds


def format_digest(articles, format="text"):
    """create a daily digest summary from a list of articles.

    format can be 'text' for plain text or 'html' for html output.
    groups articles by source and includes title, link, and date.
    """
    if not articles:
        return ""

    date_str = time.strftime("%Y-%m-%d")

    if format == "html":
        lines = [f"<h1>daily digest - {date_str}</h1>"]
        by_source = {}
        for article in articles:
            src = article.get("source", "unknown")
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(article)

        for source, items in sorted(by_source.items()):
            lines.append(f"<h2>{source}</h2><ul>")
            for item in items:
                title = item.get("title", "untitled")
                link = item.get("link", "")
                if link:
                    lines.append(f'<li><a href="{link}">{title}</a></li>')
                else:
                    lines.append(f"<li>{title}</li>")
            lines.append("</ul>")
        return "\n".join(lines)

    # plain text format
    lines = [f"daily digest - {date_str}", "=" * 40]
    by_source = {}
    for article in articles:
        src = article.get("source", "unknown")
        if src not in by_source:
            by_source[src] = []
        by_source[src].append(article)

    for source, items in sorted(by_source.items()):
        lines.append(f"\n[{source}]")
        for item in items:
            title = item.get("title", "untitled")
            link = item.get("link", "")
            line = f"  - {title}"
            if link:
                line += f"\n    {link}"
            lines.append(line)

    lines.append(f"\n{len(articles)} articles total")
    return "\n".join(lines)


def feeds_from_file(filepath):
    """load feeds from a text file (one url per line)"""
    feeds = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                feeds.append(line)
    return feeds
