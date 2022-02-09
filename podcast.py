#!/usr/bin/env python3
"""podcast rss feed parser and manager"""

import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request
from urllib.error import URLError


def fetch_podcast(feed_url):
    """fetch and parse a podcast rss feed."""
    try:
        req = Request(feed_url, headers={"User-Agent": "newk/1.0"})
        resp = urlopen(req, timeout=15)
        root = ET.fromstring(resp.read())
    except (URLError, ET.ParseError):
        return None
    channel = root.find("channel")
    if channel is None:
        return None
    podcast = {
        "title": _text(channel, "title"),
        "description": _text(channel, "description"),
        "link": _text(channel, "link"),
        "episodes": [],
    }
    for item in channel.findall("item"):
        enclosure = item.find("enclosure")
        episode = {
            "title": _text(item, "title"),
            "description": _text(item, "description"),
            "pub_date": _text(item, "pubDate"),
            "duration": _text(item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}duration"),
        }
        if enclosure is not None:
            episode["audio_url"] = enclosure.get("url", "")
            episode["type"] = enclosure.get("type", "")
            episode["length"] = int(enclosure.get("length", 0) or 0)
        podcast["episodes"].append(episode)
    return podcast


def search_episodes(podcast, query):
    """search episodes by title or description."""
    query = query.lower()
    return [
        ep for ep in podcast.get("episodes", [])
        if query in ep.get("title", "").lower()
        or query in ep.get("description", "").lower()
    ]


def _text(element, tag):
    child = element.find(tag)
    return child.text.strip() if child is not None and child.text else ""


if __name__ == "__main__":
    print("podcast parser ready")
    print("usage: fetch_podcast(url) to parse a podcast feed")
