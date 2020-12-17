#!/usr/bin/env python3
"""score feed quality based on freshness, completeness, and reliability"""

from datetime import datetime


def score_freshness(items, max_age_days=30):
    """score how recently a feed has been updated.

    returns 0-100 based on most recent item date.
    """
    if not items:
        return 0

    dates = []
    for item in items:
        date_str = item.get("date", "")
        if date_str and len(date_str) >= 10:
            try:
                dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
                dates.append(dt)
            except ValueError:
                continue

    if not dates:
        return 10  # has items but no parseable dates

    newest = max(dates)
    age_days = (datetime.now() - newest).days

    if age_days <= 1:
        return 100
    elif age_days <= 7:
        return 80
    elif age_days <= max_age_days:
        return max(20, 80 - (age_days * 2))
    return 5


def score_completeness(items):
    """score how complete the feed data is.

    checks for title, link, date, and description fields.
    """
    if not items:
        return 0

    total = 0
    for item in items:
        fields = 0
        if item.get("title"):
            fields += 30
        if item.get("link"):
            fields += 25
        if item.get("date"):
            fields += 25
        if item.get("description"):
            fields += 20
        total += fields

    return round(total / len(items))


def score_volume(items, ideal_min=5, ideal_max=50):
    """score feed volume (not too few, not too many)"""
    count = len(items)
    if count == 0:
        return 0
    if ideal_min <= count <= ideal_max:
        return 100
    if count < ideal_min:
        return max(20, count * 20)
    return max(50, 100 - (count - ideal_max))


def calculate_quality(items):
    """calculate overall quality score for a feed"""
    freshness = score_freshness(items)
    completeness = score_completeness(items)
    volume = score_volume(items)

    # weighted average
    overall = (freshness * 0.4 + completeness * 0.35 + volume * 0.25)
    return {
        "overall": round(overall),
        "freshness": freshness,
        "completeness": completeness,
        "volume": volume,
        "item_count": len(items),
    }


def rank_feeds(feed_groups):
    """rank feeds by quality score.

    feed_groups: dict of {source_url: [items]}
    returns sorted list of (url, score_dict) tuples.
    """
    scored = []
    for url, items in feed_groups.items():
        score = calculate_quality(items)
        score["source"] = url
        scored.append(score)

    scored.sort(key=lambda s: s["overall"], reverse=True)
    return scored
