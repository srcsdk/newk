#!/usr/bin/env python3
"""saved articles and bookmarks with persistent storage"""

import json
import time
from pathlib import Path

BOOKMARKS_DIR = Path.home() / ".config" / "newk"
BOOKMARKS_FILE = BOOKMARKS_DIR / "bookmarks.json"


def load_bookmarks():
    """load saved bookmarks from disk"""
    if not BOOKMARKS_FILE.exists():
        return []
    try:
        with open(BOOKMARKS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_bookmarks(bookmarks):
    """persist bookmarks to disk"""
    BOOKMARKS_DIR.mkdir(parents=True, exist_ok=True)
    with open(BOOKMARKS_FILE, "w") as f:
        json.dump(bookmarks, f, indent=2)


def add_bookmark(article):
    """bookmark an article. article should have title, link, source keys"""
    bookmarks = load_bookmarks()
    if any(b["link"] == article.get("link") for b in bookmarks):
        return False
    entry = {
        "title": article.get("title", ""),
        "link": article.get("link", ""),
        "source": article.get("source", ""),
        "category": article.get("category", ""),
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "notes": "",
    }
    bookmarks.append(entry)
    save_bookmarks(bookmarks)
    return True


def remove_bookmark(link):
    """remove a bookmark by link url"""
    bookmarks = load_bookmarks()
    before = len(bookmarks)
    bookmarks = [b for b in bookmarks if b["link"] != link]
    if len(bookmarks) < before:
        save_bookmarks(bookmarks)
        return True
    return False


def is_bookmarked(link):
    """check if an article is bookmarked"""
    return any(b["link"] == link for b in load_bookmarks())


def search_bookmarks(query):
    """search bookmarks by title or source"""
    q = query.lower()
    bookmarks = load_bookmarks()
    return [b for b in bookmarks
            if q in b["title"].lower() or q in b.get("source", "").lower()]


def get_bookmarks_by_category(category):
    """get bookmarks filtered by category"""
    return [b for b in load_bookmarks() if b.get("category") == category]


def update_notes(link, notes):
    """add notes to a bookmark"""
    bookmarks = load_bookmarks()
    for b in bookmarks:
        if b["link"] == link:
            b["notes"] = notes
            save_bookmarks(bookmarks)
            return True
    return False


def import_from_browser(bookmarks_file):
    """parse a bookmarks html file and extract urls.

    handles standard netscape bookmark format exported by
    most browsers. extracts href and link text from <a> tags.
    returns a list of dicts with 'title' and 'link' keys.
    """
    import re

    try:
        with open(bookmarks_file, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return []

    pattern = r'<[Aa]\s+[^>]*[Hh][Rr][Ee][Ff]="([^"]*)"[^>]*>(.*?)</[Aa]>'
    results = []
    for match in re.finditer(pattern, content):
        url = match.group(1).strip()
        title = match.group(2).strip()
        if url and url.startswith(("http://", "https://")):
            results.append({"title": title, "link": url})

    return results


def export_bookmarks(filepath, fmt="json"):
    """export bookmarks to file"""
    bookmarks = load_bookmarks()
    if fmt == "json":
        with open(filepath, "w") as f:
            json.dump(bookmarks, f, indent=2)
    elif fmt == "txt":
        with open(filepath, "w") as f:
            for b in bookmarks:
                f.write(f"{b['title']}\n  {b['link']}\n\n")
    return len(bookmarks)
