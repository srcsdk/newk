#!/usr/bin/env python3
"""aggregate research from multiple sources into unified feed"""

import time
from collections import defaultdict


class ResearchAggregator:
    """combine research feeds from arxiv, pubmed, and data releases."""

    def __init__(self):
        self.feeds = {}
        self.items = []
        self.read_items = set()

    def register_feed(self, name, source_type, fetcher=None):
        """register a research feed source."""
        self.feeds[name] = {
            "type": source_type,
            "fetcher": fetcher,
            "last_fetch": 0,
            "item_count": 0,
        }

    def add_item(self, source, title, url=None, summary=None,
                 category=None, published=None):
        """add a research item to the aggregated feed."""
        item_id = f"{source}:{hash(title) % 100000}"
        item = {
            "id": item_id,
            "source": source,
            "title": title,
            "url": url,
            "summary": summary,
            "category": category,
            "published": published or time.time(),
            "added": time.time(),
        }
        self.items.append(item)
        if source in self.feeds:
            self.feeds[source]["item_count"] += 1
        return item_id

    def get_feed(self, category=None, source=None, limit=50,
                 unread_only=False):
        """get aggregated feed with filters."""
        filtered = self.items
        if category:
            filtered = [i for i in filtered if i.get("category") == category]
        if source:
            filtered = [i for i in filtered if i["source"] == source]
        if unread_only:
            filtered = [i for i in filtered if i["id"] not in self.read_items]
        filtered.sort(key=lambda i: i.get("published", 0), reverse=True)
        return filtered[:limit]

    def mark_read(self, item_id):
        """mark an item as read."""
        self.read_items.add(item_id)

    def get_categories(self):
        """get all categories with item counts."""
        cats = defaultdict(int)
        for item in self.items:
            cat = item.get("category", "uncategorized")
            cats[cat] += 1
        return dict(sorted(cats.items()))

    def search(self, query):
        """search items by title or summary."""
        query = query.lower()
        return [
            item for item in self.items
            if query in item.get("title", "").lower()
            or query in (item.get("summary") or "").lower()
        ]

    def deduplicate(self):
        """remove duplicate items by title similarity."""
        seen_titles = {}
        unique = []
        for item in self.items:
            title_key = item["title"].lower().strip()
            if title_key not in seen_titles:
                seen_titles[title_key] = True
                unique.append(item)
        removed = len(self.items) - len(unique)
        self.items = unique
        return removed

    def summary(self):
        """get aggregator summary."""
        unread = len([i for i in self.items if i["id"] not in self.read_items])
        return {
            "sources": len(self.feeds),
            "total_items": len(self.items),
            "unread": unread,
            "categories": len(self.get_categories()),
        }


if __name__ == "__main__":
    agg = ResearchAggregator()
    agg.register_feed("arxiv", "preprint")
    agg.register_feed("pubmed", "medical")
    agg.add_item("arxiv", "new attention mechanism", category="ai_ml")
    agg.add_item("pubmed", "sleep study results", category="health")
    agg.add_item("arxiv", "quantum error correction", category="physics")
    summary = agg.summary()
    for key, val in summary.items():
        print(f"  {key}: {val}")
