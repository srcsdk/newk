#!/usr/bin/env python3
"""import and export feeds in opml and json formats"""

import json
import xml.etree.ElementTree as ET


def export_opml(feeds, output_path):
    """export feed list to opml format."""
    opml = ET.Element("opml", version="2.0")
    head = ET.SubElement(opml, "head")
    ET.SubElement(head, "title").text = "newk feeds"
    body = ET.SubElement(opml, "body")
    categories = {}
    for feed in feeds:
        cat = feed.get("category", "uncategorized")
        categories.setdefault(cat, []).append(feed)
    for cat, cat_feeds in categories.items():
        outline = ET.SubElement(body, "outline", text=cat)
        for feed in cat_feeds:
            ET.SubElement(outline, "outline",
                          text=feed.get("title", ""),
                          xmlUrl=feed.get("url", ""),
                          htmlUrl=feed.get("site_url", ""),
                          type="rss")
    tree = ET.ElementTree(opml)
    ET.indent(tree, space="  ")
    tree.write(output_path, encoding="unicode", xml_declaration=True)
    return output_path


def import_opml(opml_path):
    """import feeds from opml file."""
    try:
        tree = ET.parse(opml_path)
    except ET.ParseError:
        return []
    root = tree.getroot()
    feeds = []
    for outline in root.iter("outline"):
        url = outline.get("xmlUrl", "")
        if url:
            parent = _find_parent(root, outline)
            category = parent.get("text", "") if parent is not None else ""
            feeds.append({
                "title": outline.get("text", ""),
                "url": url,
                "site_url": outline.get("htmlUrl", ""),
                "category": category,
            })
    return feeds


def _find_parent(root, child):
    """find parent element of a child in xml tree."""
    for parent in root.iter():
        if child in list(parent):
            return parent
    return None


def export_json(feeds, output_path):
    """export feeds to json."""
    with open(output_path, "w") as f:
        json.dump(feeds, f, indent=2)
    return output_path


def import_json(json_path):
    """import feeds from json."""
    with open(json_path) as f:
        return json.load(f)


if __name__ == "__main__":
    feeds = [
        {"title": "hacker news", "url": "https://hnrss.org/frontpage", "category": "tech"},
        {"title": "lobsters", "url": "https://lobste.rs/rss", "category": "tech"},
        {"title": "arxiv cs", "url": "http://arxiv.org/rss/cs", "category": "research"},
    ]
    opml_path = "/tmp/newk_feeds.opml"
    export_opml(feeds, opml_path)
    print(f"exported {len(feeds)} feeds to {opml_path}")
    imported = import_opml(opml_path)
    print(f"imported back: {len(imported)} feeds")
