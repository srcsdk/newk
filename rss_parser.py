#!/usr/bin/env python3
"""rss and atom feed parsing"""

import re
import xml.etree.ElementTree as ET


def parse_rss(xml_content):
    """parse rss 2.0 feed content."""
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return {"title": "", "items": []}
    channel = root.find("channel")
    if channel is None:
        return {"title": "", "items": []}
    title = _text(channel, "title")
    items = []
    for item in channel.findall("item"):
        entry = {
            "title": _text(item, "title"),
            "link": _text(item, "link"),
            "description": _clean_html(_text(item, "description")),
            "pub_date": _text(item, "pubDate"),
            "guid": _text(item, "guid"),
        }
        items.append(entry)
    return {"title": title, "items": items}


def parse_atom(xml_content):
    """parse atom feed content."""
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return {"title": "", "items": []}
    title_el = root.find("atom:title", ns)
    title = title_el.text if title_el is not None else ""
    items = []
    for entry in root.findall("atom:entry", ns):
        link_el = entry.find("atom:link", ns)
        link = link_el.get("href", "") if link_el is not None else ""
        title_el = entry.find("atom:title", ns)
        summary_el = entry.find("atom:summary", ns)
        updated_el = entry.find("atom:updated", ns)
        items.append({
            "title": title_el.text if title_el is not None else "",
            "link": link,
            "description": summary_el.text if summary_el is not None else "",
            "pub_date": updated_el.text if updated_el is not None else "",
        })
    return {"title": title, "items": items}


def detect_feed_type(xml_content):
    """detect whether content is rss or atom."""
    if "<rss" in xml_content[:500]:
        return "rss"
    elif "http://www.w3.org/2005/Atom" in xml_content[:500]:
        return "atom"
    return "unknown"


def parse_feed(xml_content):
    """auto-detect and parse feed."""
    feed_type = detect_feed_type(xml_content)
    if feed_type == "rss":
        return parse_rss(xml_content)
    elif feed_type == "atom":
        return parse_atom(xml_content)
    return {"title": "", "items": []}


def _text(element, tag):
    """safely get text from xml element."""
    child = element.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return ""


def _clean_html(text):
    """remove html tags from text."""
    return re.sub(r"<[^>]+>", "", text).strip()


if __name__ == "__main__":
    sample_rss = """<?xml version="1.0"?>
    <rss version="2.0">
    <channel>
    <title>test feed</title>
    <item>
      <title>article one</title>
      <link>https://example.com/1</link>
      <description>first article content</description>
    </item>
    <item>
      <title>article two</title>
      <link>https://example.com/2</link>
      <description>second article content</description>
    </item>
    </channel>
    </rss>"""
    result = parse_feed(sample_rss)
    print(f"feed: {result['title']}")
    for item in result["items"]:
        print(f"  {item['title']}: {item['link']}")
