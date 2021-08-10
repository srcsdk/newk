#!/usr/bin/env python3
"""validate feed urls and check for common issues"""

import re
from urllib.parse import urlparse


def validate_url(url):
    """check if url is valid and reachable format."""
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


def detect_feed_type(content):
    """detect whether content is rss, atom, or unknown."""
    if "<rss" in content[:500].lower():
        return "rss"
    elif "<feed" in content[:500].lower():
        return "atom"
    elif "rdf:rdf" in content[:500].lower():
        return "rdf"
    return "unknown"


def find_feed_links(html):
    """extract feed urls from html link tags."""
    pattern = r'<link[^>]+type=["']application/(rss|atom)\+xml["'][^>]*/>'
    matches = re.findall(pattern, html, re.IGNORECASE)
    hrefs = re.findall(
        r'<link[^>]+type=["']application/(?:rss|atom)\+xml["'][^>]*'
        r'href=["']([^"']+)["']',
        html, re.IGNORECASE
    )
    return hrefs


def check_feed_health(entries):
    """check feed for common issues."""
    issues = []
    if not entries:
        issues.append("no entries found")
        return issues
    if len(entries) < 3:
        issues.append("very few entries, feed may be inactive")
    dates = [e.get("date") for e in entries if e.get("date")]
    if not dates:
        issues.append("no dates found in entries")
    return issues


if __name__ == "__main__":
    print(validate_url("https://example.com/feed.xml"))
    print(detect_feed_type("<rss version=\"2.0\"><channel>"))
