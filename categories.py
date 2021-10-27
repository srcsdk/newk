#!/usr/bin/env python3
"""category management with user-defined custom feeds"""

import json
import os

CATEGORIES_FILE = os.path.join(os.path.dirname(__file__), "categories.json")

DEFAULT_CATEGORIES = {
    "technology": {"feeds": [], "keywords": ["tech", "software", "hardware", "ai"]},
    "science": {"feeds": [], "keywords": ["research", "study", "discovery"]},
    "security": {"feeds": [], "keywords": ["vulnerability", "exploit", "cyber"]},
    "finance": {"feeds": [], "keywords": ["market", "stock", "economy"]},
    "health": {"feeds": [], "keywords": ["medical", "health", "clinical"]},
}


def load_categories():
    """load categories from file or return defaults."""
    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, "r") as f:
            return json.load(f)
    return dict(DEFAULT_CATEGORIES)


def save_categories(categories):
    """save categories to file."""
    with open(CATEGORIES_FILE, "w") as f:
        json.dump(categories, f, indent=2)


def add_category(name, keywords=None, feeds=None):
    """add a new custom category."""
    cats = load_categories()
    cats[name] = {
        "feeds": feeds or [],
        "keywords": keywords or [],
        "custom": True,
    }
    save_categories(cats)
    return cats[name]


def add_feed_to_category(category, feed_url):
    """assign a feed to a category."""
    cats = load_categories()
    if category in cats:
        if feed_url not in cats[category]["feeds"]:
            cats[category]["feeds"].append(feed_url)
            save_categories(cats)
    return cats.get(category)


def auto_categorize(article, categories=None):
    """auto-assign category based on keyword matching."""
    if categories is None:
        categories = load_categories()
    text = (article.get("title", "") + " " + article.get("abstract", "")).lower()
    scores = {}
    for cat_name, cat_info in categories.items():
        matches = sum(1 for kw in cat_info.get("keywords", []) if kw in text)
        if matches > 0:
            scores[cat_name] = matches
    if scores:
        return max(scores, key=scores.get)
    return "uncategorized"


def category_stats(categories=None):
    """get statistics for all categories."""
    if categories is None:
        categories = load_categories()
    return {
        name: {"feeds": len(info.get("feeds", [])),
               "keywords": len(info.get("keywords", [])),
               "custom": info.get("custom", False)}
        for name, info in categories.items()
    }


if __name__ == "__main__":
    cats = load_categories()
    print(f"categories: {len(cats)}")
    for name, info in cats.items():
        print(f"  {name}: {len(info.get('keywords', []))} keywords")
