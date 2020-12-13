#!/usr/bin/env python3
"""extended rss parser supporting rss 1.0, rdf, and json feed formats"""

import json
import xml.etree.ElementTree as ET
from datetime import datetime


def parse_rss1(raw_bytes, source_url):
    """parse rss 1.0 / rdf feed format"""
    if raw_bytes is None:
        return []

    try:
        root = ET.fromstring(raw_bytes)
    except ET.ParseError:
        return []

    items = []
    ns = {"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
          "rss": "http://purl.org/rss/1.0/",
          "dc": "http://purl.org/dc/elements/1.1/"}

    for item in root.findall(".//rss:item", ns):
        title_el = item.find("rss:title", ns)
        link_el = item.find("rss:link", ns)
        desc_el = item.find("rss:description", ns)
        date_el = item.find("dc:date", ns)

        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        link = link_el.text.strip() if link_el is not None and link_el.text else ""
        desc = desc_el.text.strip() if desc_el is not None and desc_el.text else ""
        date = date_el.text.strip() if date_el is not None and date_el.text else ""

        if title:
            items.append({
                "title": title,
                "link": link,
                "date": date[:19],
                "description": desc[:500],
                "source": source_url,
                "format": "rss1",
            })

    return items


def parse_json_feed(raw_bytes, source_url):
    """parse json feed format (jsonfeed.org spec)"""
    if raw_bytes is None:
        return []

    try:
        data = json.loads(raw_bytes)
    except (json.JSONDecodeError, ValueError):
        return []

    items = []
    for entry in data.get("items", []):
        title = entry.get("title", "")
        url = entry.get("url", entry.get("external_url", ""))
        date = entry.get("date_published", "")
        summary = entry.get("summary", entry.get("content_text", ""))

        if title:
            items.append({
                "title": title,
                "link": url,
                "date": date[:19] if date else "",
                "description": (summary or "")[:500],
                "source": source_url,
                "format": "json_feed",
            })

    return items


def detect_format(raw_bytes):
    """detect feed format from content"""
    if raw_bytes is None:
        return "unknown"

    content = raw_bytes[:500].decode("utf-8", errors="replace").strip()

    if content.startswith("{"):
        return "json_feed"
    if "rdf:RDF" in content or "xmlns=\"http://purl.org/rss/1.0/\"" in content:
        return "rss1"
    if "<rss" in content:
        return "rss2"
    if "<feed" in content and "xmlns=\"http://www.w3.org/2005/Atom\"" in content:
        return "atom"
    return "unknown"


def parse_auto(raw_bytes, source_url):
    """auto-detect format and parse accordingly"""
    fmt = detect_format(raw_bytes)
    if fmt == "json_feed":
        return parse_json_feed(raw_bytes, source_url)
    elif fmt == "rss1":
        return parse_rss1(raw_bytes, source_url)
    return []
