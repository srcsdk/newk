#!/usr/bin/env python3
"""category engine for organizing feeds by topic depth"""

import json
import os


class CategoryEngine:
    """manage hierarchical feed categories with quality scoring."""

    def __init__(self, config_path=None):
        self.categories = {}
        self.sources = {}
        if config_path and os.path.isfile(config_path):
            self._load_config(config_path)
        else:
            self._init_defaults()

    def _init_defaults(self):
        """set up default category tree."""
        self.categories = {
            "technology": {
                "subcategories": [
                    "ai_ml", "cybersecurity", "systems", "web",
                    "mobile", "devops", "databases", "languages",
                ],
                "sources": [],
            },
            "science": {
                "subcategories": [
                    "physics", "biology", "chemistry", "astronomy",
                    "mathematics", "neuroscience",
                ],
                "sources": [],
            },
            "finance": {
                "subcategories": [
                    "markets", "economics", "crypto", "policy",
                    "data_releases",
                ],
                "sources": [],
            },
            "health": {
                "subcategories": [
                    "research", "nutrition", "fitness", "mental_health",
                ],
                "sources": [],
            },
        }

    def _load_config(self, path):
        """load categories from config file."""
        with open(path) as f:
            data = json.load(f)
        self.categories = data.get("categories", {})

    def add_category(self, name, subcategories=None):
        """add a new top-level category."""
        self.categories[name] = {
            "subcategories": subcategories or [],
            "sources": [],
        }

    def add_source(self, category, source_url, quality_score=0.5):
        """add a source to a category."""
        if category not in self.sources:
            self.sources[category] = []
        self.sources[category].append({
            "url": source_url,
            "quality": quality_score,
            "fetch_count": 0,
            "error_count": 0,
        })

    def get_sources(self, category, min_quality=0.0):
        """get sources for category above quality threshold."""
        sources = self.sources.get(category, [])
        return [s for s in sources if s["quality"] >= min_quality]

    def update_quality(self, category, source_url, adjustment):
        """adjust source quality score based on content value."""
        for source in self.sources.get(category, []):
            if source["url"] == source_url:
                source["quality"] = max(0, min(1, source["quality"] + adjustment))
                break

    def list_categories(self):
        """list all categories with subcategory counts."""
        return {
            name: len(data.get("subcategories", []))
            for name, data in self.categories.items()
        }

    def search_categories(self, query):
        """find categories matching query string."""
        query = query.lower()
        matches = []
        for name, data in self.categories.items():
            if query in name:
                matches.append(name)
            for sub in data.get("subcategories", []):
                if query in sub:
                    matches.append(f"{name}/{sub}")
        return matches

    def export_config(self, path):
        """save categories to config file."""
        data = {"categories": self.categories, "sources": self.sources}
        with open(path, "w") as f:
            json.dump(data, f, indent=2)


if __name__ == "__main__":
    engine = CategoryEngine()
    cats = engine.list_categories()
    for name, count in cats.items():
        print(f"  {name}: {count} subcategories")
    results = engine.search_categories("cyber")
    print(f"search 'cyber': {results}")
