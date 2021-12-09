#!/usr/bin/env python3
"""reading history and read/unread tracking"""

import hashlib
import json
import time
from pathlib import Path

READING_DIR = Path.home() / ".config" / "newk"
READING_FILE = READING_DIR / "reading_history.json"
MAX_HISTORY = 2000


def _article_id(article):
    """generate a unique id for an article"""
    key = article.get("link", article.get("title", ""))
    return hashlib.md5(key.encode()).hexdigest()[:12]


def load_history():
    """load reading history"""
    if not READING_FILE.exists():
        return {"read": {}, "reading_time": {}}
    try:
        with open(READING_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"read": {}, "reading_time": {}}


def save_history(history):
    """save reading history"""
    READING_DIR.mkdir(parents=True, exist_ok=True)

    # trim if too large
    if len(history["read"]) > MAX_HISTORY:
        sorted_items = sorted(history["read"].items(),
                              key=lambda x: x[1].get("read_at", ""))
        to_keep = dict(sorted_items[-MAX_HISTORY:])
        history["read"] = to_keep

    with open(READING_FILE, "w") as f:
        json.dump(history, f, indent=2)


def mark_read(article):
    """mark an article as read"""
    history = load_history()
    aid = _article_id(article)
    history["read"][aid] = {
        "title": article.get("title", "")[:100],
        "link": article.get("link", ""),
        "read_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": article.get("source", ""),
    }
    save_history(history)


def mark_unread(article):
    """mark an article as unread"""
    history = load_history()
    aid = _article_id(article)
    if aid in history["read"]:
        del history["read"][aid]
        save_history(history)


def is_read(article):
    """check if an article has been read"""
    history = load_history()
    return _article_id(article) in history["read"]


def filter_unread(articles):
    """filter articles to only unread ones"""
    history = load_history()
    return [a for a in articles if _article_id(a) not in history["read"]]


def filter_read(articles):
    """filter articles to only read ones"""
    history = load_history()
    return [a for a in articles if _article_id(a) in history["read"]]


def get_recent_reads(limit=20):
    """get recently read articles"""
    history = load_history()
    items = sorted(history["read"].values(),
                   key=lambda x: x.get("read_at", ""),
                   reverse=True)
    return items[:limit]


def reading_stats():
    """get reading statistics"""
    history = load_history()
    total = len(history["read"])

    # articles read per day (last 7 days)
    daily = {}
    for item in history["read"].values():
        day = item.get("read_at", "")[:10]
        if day:
            daily[day] = daily.get(day, 0) + 1

    sorted_days = sorted(daily.keys())[-7:]
    recent_daily = {d: daily.get(d, 0) for d in sorted_days}

    # top sources read
    sources = {}
    for item in history["read"].values():
        src = item.get("source", "unknown")
        sources[src] = sources.get(src, 0) + 1
    top_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_read": total,
        "recent_daily": recent_daily,
        "top_sources": top_sources,
    }


def clear_history():
    """clear all reading history"""
    save_history({"read": {}, "reading_time": {}})
