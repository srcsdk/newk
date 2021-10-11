#!/usr/bin/env python3
"""feed statistics dashboard - articles per day, top sources"""

import json
import time
from collections import Counter, defaultdict
from pathlib import Path

STATS_DIR = Path.home() / ".config" / "newk"
STATS_FILE = STATS_DIR / "feed_stats.json"


def load_stats():
    """load accumulated statistics"""
    if not STATS_FILE.exists():
        return {"daily": {}, "sources": {}, "categories": {}, "total_articles": 0}
    try:
        with open(STATS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"daily": {}, "sources": {}, "categories": {}, "total_articles": 0}


def save_stats(stats):
    """save statistics to disk"""
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)


def record_articles(articles):
    """record article statistics from a fetch"""
    stats = load_stats()
    today = time.strftime("%Y-%m-%d")

    if today not in stats["daily"]:
        stats["daily"][today] = 0
    stats["daily"][today] += len(articles)
    stats["total_articles"] += len(articles)

    for article in articles:
        source = article.get("source", "unknown")
        if source not in stats["sources"]:
            stats["sources"][source] = 0
        stats["sources"][source] += 1

        category = article.get("category", "uncategorized")
        if category not in stats["categories"]:
            stats["categories"][category] = 0
        stats["categories"][category] += 1

    # trim daily stats to last 90 days
    sorted_days = sorted(stats["daily"].keys())
    if len(sorted_days) > 90:
        for day in sorted_days[:-90]:
            del stats["daily"][day]

    save_stats(stats)
    return stats


def top_sources(n=10):
    """get top n sources by article count"""
    stats = load_stats()
    sorted_sources = sorted(stats["sources"].items(),
                            key=lambda x: x[1], reverse=True)
    return sorted_sources[:n]


def top_categories(n=10):
    """get top n categories by article count"""
    stats = load_stats()
    sorted_cats = sorted(stats["categories"].items(),
                         key=lambda x: x[1], reverse=True)
    return sorted_cats[:n]


def daily_average(days=30):
    """calculate average articles per day over recent period"""
    stats = load_stats()
    daily = stats.get("daily", {})
    sorted_days = sorted(daily.keys())[-days:]
    if not sorted_days:
        return 0
    total = sum(daily[d] for d in sorted_days)
    return total / len(sorted_days)


def weekly_trend():
    """show articles per day for the last 7 days"""
    stats = load_stats()
    daily = stats.get("daily", {})
    sorted_days = sorted(daily.keys())[-7:]
    return [(d, daily.get(d, 0)) for d in sorted_days]


def format_dashboard():
    """format statistics for display"""
    stats = load_stats()
    lines = ["feed statistics dashboard", ""]

    lines.append(f"total articles tracked: {stats['total_articles']}")
    lines.append(f"average per day (30d): {daily_average():.1f}")
    lines.append("")

    lines.append("top sources:")
    for source, count in top_sources(5):
        lines.append(f"  {source}: {count}")
    lines.append("")

    lines.append("top categories:")
    for cat, count in top_categories(5):
        lines.append(f"  {cat}: {count}")
    lines.append("")

    lines.append("recent daily:")
    for day, count in weekly_trend():
        bar = "#" * min(count, 50)
        lines.append(f"  {day}: {count:>4} {bar}")

    return "\n".join(lines)
