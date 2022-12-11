#!/usr/bin/env python3
"""discover rss feeds from websites"""

import re
from urllib.request import urlopen, Request
from urllib.error import URLError


def discover_feeds(url):
    """discover rss/atom feeds from a website url."""
    try:
        req = Request(url, headers={"User-Agent": "newk/1.0"})
        resp = urlopen(req, timeout=15)
        html = resp.read().decode(errors="replace")
    except (URLError, OSError):
        return []
    feeds = []
    link_pattern = re.compile(
        r"<link[^>]+type=[\"']application/(rss|atom)\+xml[\"'][^>]*>",
        re.IGNORECASE,
    )
    for match in link_pattern.finditer(html):
        tag = match.group(0)
        href = _extract_attr(tag, "href")
        title = _extract_attr(tag, "title")
        feed_type = match.group(1)
        if href:
            if not href.startswith("http"):
                href = _resolve_url(url, href)
            feeds.append({
                "url": href,
                "title": title or "",
                "type": feed_type,
            })
    common_paths = ["/feed", "/rss", "/atom.xml", "/feed.xml", "/rss.xml", "/index.xml"]
    base = url.rstrip("/")
    for path in common_paths:
        feed_url = base + path
        if _is_valid_feed(feed_url):
            feeds.append({"url": feed_url, "title": "", "type": "discovered"})
            break
    return feeds


def _extract_attr(tag, attr):
    """extract attribute value from html tag."""
    pattern = re.compile(attr + r'=["\x27]([^"\x27]+)["\x27]', re.IGNORECASE)
    match = pattern.search(tag)
    return match.group(1) if match else ""


def _resolve_url(base, path):
    """resolve relative url against base."""
    if path.startswith("//"):
        return "https:" + path
    from urllib.parse import urljoin
    return urljoin(base, path)


def _is_valid_feed(url):
    """check if url returns valid feed content."""
    try:
        req = Request(url, headers={"User-Agent": "newk/1.0"})
        resp = urlopen(req, timeout=5)
        content = resp.read(500).decode(errors="replace")
        return "<rss" in content or "<feed" in content or "<channel" in content
    except (URLError, OSError):
        return False


if __name__ == "__main__":
    print("feed discovery ready")
    print("usage: discover_feeds('https://example.com')")
