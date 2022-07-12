#!/usr/bin/env python3
"""content archival system for permanent storage"""

import os
import json
import time
import hashlib


class Archive:
    """archive articles for permanent storage."""

    def __init__(self, archive_dir=None):
        if archive_dir is None:
            archive_dir = os.path.expanduser("~/.newk/archive")
        self.archive_dir = archive_dir
        self.index_file = os.path.join(archive_dir, "index.json")
        os.makedirs(archive_dir, exist_ok=True)
        self.index = self._load_index()

    def _load_index(self):
        if os.path.isfile(self.index_file):
            with open(self.index_file) as f:
                return json.load(f)
        return {}

    def _save_index(self):
        with open(self.index_file, "w") as f:
            json.dump(self.index, f, indent=2)

    def archive_article(self, article, content=""):
        """archive an article with its content."""
        key = hashlib.md5(article.get("url", article.get("title", "")).encode()).hexdigest()[:12]
        entry = {
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "source": article.get("source", ""),
            "category": article.get("category", ""),
            "archived_at": time.strftime("%Y-%m-%d %H:%M"),
            "tags": article.get("tags", []),
        }
        if content:
            content_path = os.path.join(self.archive_dir, f"{key}.txt")
            with open(content_path, "w") as f:
                f.write(content)
            entry["content_file"] = content_path
        self.index[key] = entry
        self._save_index()
        return key

    def get_article(self, key):
        """retrieve an archived article."""
        entry = self.index.get(key)
        if not entry:
            return None
        content_path = entry.get("content_file", "")
        if content_path and os.path.isfile(content_path):
            with open(content_path) as f:
                entry["content"] = f.read()
        return entry

    def search(self, query):
        """search archived articles."""
        query = query.lower()
        results = []
        for key, entry in self.index.items():
            if (query in entry.get("title", "").lower()
                    or query in entry.get("source", "").lower()
                    or any(query in t.lower() for t in entry.get("tags", []))):
                results.append({"key": key, **entry})
        return results

    def by_category(self, category):
        """get archived articles by category."""
        return [
            {"key": k, **v} for k, v in self.index.items()
            if v.get("category") == category
        ]

    def stats(self):
        """archive statistics."""
        categories = {}
        for entry in self.index.values():
            cat = entry.get("category", "uncategorized")
            categories[cat] = categories.get(cat, 0) + 1
        return {"total": len(self.index), "categories": categories}


if __name__ == "__main__":
    arch = Archive("/tmp/newk_archive")
    key = arch.archive_article(
        {"title": "test article", "url": "https://example.com", "category": "tech"},
        content="this is the article content"
    )
    print(f"archived: {key}")
    print(f"stats: {arch.stats()}")
    retrieved = arch.get_article(key)
    print(f"retrieved: {retrieved['title']}")
