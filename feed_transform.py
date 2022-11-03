#!/usr/bin/env python3
"""transform and normalize feed data"""

import re
import html
from datetime import datetime


def normalize_article(article):
    """normalize article data from different feed formats."""
    normalized = {
        "title": _clean_text(article.get("title", "")),
        "description": _clean_text(article.get("description", article.get("summary", ""))),
        "url": article.get("link", article.get("url", article.get("id", ""))),
        "author": article.get("author", article.get("creator", "")),
        "date": _parse_date(article.get("pub_date", article.get("published", article.get("updated", "")))),
        "source": article.get("source", article.get("feed_title", "")),
        "categories": _extract_categories(article),
    }
    return normalized


def _clean_text(text):
    """remove html tags and decode entities."""
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _parse_date(date_str):
    """parse various date formats to iso format."""
    if not date_str:
        return ""
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    date_str = str(date_str).strip()
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str[:len(fmt) + 10], fmt)
            return dt.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            continue
    return date_str[:19]


def _extract_categories(article):
    """extract categories/tags from article."""
    cats = []
    for key in ("categories", "tags", "category"):
        val = article.get(key)
        if isinstance(val, list):
            cats.extend(str(v) for v in val)
        elif isinstance(val, str) and val:
            cats.append(val)
    return cats


def batch_normalize(articles):
    """normalize a batch of articles."""
    return [normalize_article(a) for a in articles]


if __name__ == "__main__":
    raw = {
        "title": "Test &amp; Article <b>bold</b>",
        "description": "<p>This is a <a href='#'>test</a> description</p>",
        "pub_date": "Mon, 15 Aug 2022 12:00:00 +0000",
        "link": "https://example.com/article",
        "categories": ["tech", "python"],
    }
    normalized = normalize_article(raw)
    print(f"title: {normalized['title']}")
    print(f"date: {normalized['date']}")
    print(f"categories: {normalized['categories']}")
