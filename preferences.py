#!/usr/bin/env python3
"""user preferences for personalized feed ranking and read history"""

import hashlib
import json
import os
from datetime import datetime

PREFS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_data")
PREFS_FILE = os.path.join(PREFS_DIR, "preferences.json")

DEFAULT_PREFS = {
    "interests": [],
    "pinned_categories": [],
    "read_history": {},
    "feed_weights": {},
    "created": "",
    "updated": "",
}


def _ensure_dir():
    """create user data directory if needed"""
    if not os.path.exists(PREFS_DIR):
        os.makedirs(PREFS_DIR, exist_ok=True)


def load_preferences():
    """load user preferences from disk"""
    if not os.path.exists(PREFS_FILE):
        return dict(DEFAULT_PREFS)
    try:
        with open(PREFS_FILE, "r") as f:
            data = json.load(f)
        for key, val in DEFAULT_PREFS.items():
            if key not in data:
                data[key] = val if not isinstance(val, dict) else dict(val)
        return data
    except (json.JSONDecodeError, ValueError, OSError):
        return dict(DEFAULT_PREFS)


def save_preferences(prefs):
    """save preferences to disk"""
    _ensure_dir()
    prefs["updated"] = datetime.now().isoformat()
    if not prefs.get("created"):
        prefs["created"] = prefs["updated"]
    with open(PREFS_FILE, "w") as f:
        json.dump(prefs, f, indent=2)


def add_interest(keyword):
    """add an interest keyword for relevance scoring"""
    prefs = load_preferences()
    kw = keyword.lower().strip()
    if kw and kw not in prefs["interests"]:
        prefs["interests"].append(kw)
        save_preferences(prefs)
    return prefs


def remove_interest(keyword):
    """remove an interest keyword"""
    prefs = load_preferences()
    kw = keyword.lower().strip()
    if kw in prefs["interests"]:
        prefs["interests"].remove(kw)
        save_preferences(prefs)
    return prefs


def pin_category(category_name):
    """pin a category so it shows as a tab"""
    prefs = load_preferences()
    cat = category_name.lower().strip()
    if cat and cat not in prefs["pinned_categories"]:
        prefs["pinned_categories"].append(cat)
        save_preferences(prefs)
    return prefs


def unpin_category(category_name):
    """remove a pinned category tab"""
    prefs = load_preferences()
    cat = category_name.lower().strip()
    if cat in prefs["pinned_categories"]:
        prefs["pinned_categories"].remove(cat)
        save_preferences(prefs)
    return prefs


def _item_id(item):
    """generate unique id for a feed item"""
    key = (item.get("title", "") + item.get("link", "")).lower().strip()
    return hashlib.md5(key.encode()).hexdigest()


def mark_read(item):
    """mark an article as read"""
    prefs = load_preferences()
    iid = _item_id(item)
    prefs["read_history"][iid] = datetime.now().isoformat()
    if len(prefs["read_history"]) > 5000:
        entries = sorted(prefs["read_history"].items(), key=lambda x: x[1])
        prefs["read_history"] = dict(entries[-3000:])
    save_preferences(prefs)


def is_read(item):
    """check if an article has been read"""
    prefs = load_preferences()
    return _item_id(item) in prefs["read_history"]


def score_relevance(item, prefs=None):
    """score item relevance based on user interests.

    returns 0-100 based on how many interests match the item text.
    """
    if prefs is None:
        prefs = load_preferences()

    interests = prefs.get("interests", [])
    if not interests:
        return 50

    title = item.get("title", "").lower()
    desc = item.get("description", "").lower()
    category = item.get("category", "").lower()
    subcategory = item.get("subcategory", "").lower()
    text = title + " " + desc + " " + category + " " + subcategory

    matches = sum(1 for kw in interests if kw in text)
    if matches == 0:
        return 10

    weight = prefs.get("feed_weights", {}).get(item.get("source", ""), 1.0)
    score = min(100, int((matches / len(interests)) * 80 + 20))
    return min(100, int(score * weight))


def rank_by_relevance(items, prefs=None):
    """sort items by relevance score, highest first"""
    if prefs is None:
        prefs = load_preferences()
    scored = [(score_relevance(item, prefs), item) for item in items]
    scored.sort(key=lambda x: (-x[0], x[1].get("date", "") or ""), reverse=False)
    return [item for _, item in scored]
