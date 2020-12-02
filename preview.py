#!/usr/bin/env python3
"""generate feed previews with truncated summaries"""

import html
import re
import sys


def strip_html(text):
    """remove html tags from text"""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = html.unescape(clean)
    return clean.strip()


def truncate_text(text, max_length=200):
    """truncate text to max_length, breaking at word boundary"""
    if len(text) <= max_length:
        return text
    truncated = text[:max_length]
    last_space = truncated.rfind(" ")
    if last_space > max_length * 0.6:
        truncated = truncated[:last_space]
    return truncated + "..."


def generate_preview(item, summary_length=200):
    """generate a preview dict from a feed item"""
    title = item.get("title", "")
    description = item.get("description", "")
    link = item.get("link", "")
    date = item.get("date", "")[:10]

    clean_desc = strip_html(description)
    summary = truncate_text(clean_desc, summary_length)

    return {
        "title": title[:120],
        "summary": summary,
        "link": link,
        "date": date,
        "source": item.get("source", ""),
        "category": item.get("category", ""),
    }


def generate_previews(items, summary_length=200, limit=50):
    """generate previews for a list of feed items"""
    return [generate_preview(item, summary_length) for item in items[:limit]]


def print_previews(previews):
    """display previews in terminal"""
    for p in previews:
        print(f"  {p['date']}  {p['title'][:80]}")
        if p["summary"]:
            print(f"           {p['summary'][:100]}")
        print()


if __name__ == "__main__":
    try:
        from scrape import scrape_all
        items = scrape_all(verbose=False)
        previews = generate_previews(items, limit=10)
        print_previews(previews)
    except ImportError:
        print("run from newk directory", file=sys.stderr)
        sys.exit(1)
