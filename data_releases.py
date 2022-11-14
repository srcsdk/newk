#!/usr/bin/env python3
"""track and aggregate research data releases"""

import json
import os
import time


class DataReleaseTracker:
    """track data releases from research organizations."""

    def __init__(self, data_dir=None):
        self.data_dir = data_dir or os.path.expanduser("~/.newk/releases")
        self.sources = {}
        self.releases = []

    def add_source(self, name, source_type, url=None, category=None):
        """register a data release source."""
        self.sources[name] = {
            "type": source_type,
            "url": url,
            "category": category or "general",
            "last_check": 0,
        }

    def record_release(self, source, title, url=None, data_type=None,
                       description=None):
        """record a new data release."""
        release = {
            "source": source,
            "title": title,
            "url": url,
            "data_type": data_type,
            "description": description,
            "recorded_at": time.time(),
            "read": False,
        }
        self.releases.append(release)
        return release

    def get_releases(self, category=None, source=None, unread_only=False):
        """get releases with optional filters."""
        filtered = self.releases
        if category:
            cat_sources = [
                name for name, info in self.sources.items()
                if info["category"] == category
            ]
            filtered = [r for r in filtered if r["source"] in cat_sources]
        if source:
            filtered = [r for r in filtered if r["source"] == source]
        if unread_only:
            filtered = [r for r in filtered if not r["read"]]
        return sorted(filtered, key=lambda r: r["recorded_at"], reverse=True)

    def mark_read(self, index):
        """mark a release as read."""
        if 0 <= index < len(self.releases):
            self.releases[index]["read"] = True

    def get_categories(self):
        """get all categories with source counts."""
        cats = {}
        for info in self.sources.values():
            cat = info["category"]
            cats[cat] = cats.get(cat, 0) + 1
        return cats

    def export(self, filepath):
        """export releases to json."""
        with open(filepath, "w") as f:
            json.dump({
                "sources": self.sources,
                "releases": self.releases,
            }, f, indent=2)

    def load(self, filepath):
        """load releases from json."""
        if os.path.isfile(filepath):
            with open(filepath) as f:
                data = json.load(f)
            self.sources = data.get("sources", {})
            self.releases = data.get("releases", [])

    def summary(self):
        """get tracker summary."""
        unread = sum(1 for r in self.releases if not r["read"])
        return {
            "sources": len(self.sources),
            "total_releases": len(self.releases),
            "unread": unread,
            "categories": self.get_categories(),
        }


if __name__ == "__main__":
    tracker = DataReleaseTracker()
    tracker.add_source("arxiv", "preprint", category="research")
    tracker.add_source("bls", "government", category="economics")
    tracker.add_source("pubmed", "medical", category="health")
    tracker.record_release("arxiv", "new transformer architecture")
    tracker.record_release("bls", "employment report q3 2022")
    summary = tracker.summary()
    for key, val in summary.items():
        print(f"  {key}: {val}")
