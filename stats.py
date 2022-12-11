#!/usr/bin/env python3
"""reading statistics and analytics"""

import json
import os


class ReadingStats:
    """track and analyze reading statistics."""

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.newk")
        self.stats_file = os.path.join(data_dir, "stats.json")
        os.makedirs(data_dir, exist_ok=True)
        self.data = self._load()

    def _load(self):
        if os.path.isfile(self.stats_file):
            with open(self.stats_file) as f:
                return json.load(f)
        return {"daily": {}, "sources": {}, "categories": {}, "total_read": 0}

    def _save(self):
        with open(self.stats_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def record(self, article, date=None):
        """record reading an article."""
        import time
        if date is None:
            date = time.strftime("%Y-%m-%d")
        self.data["daily"][date] = self.data["daily"].get(date, 0) + 1
        source = article.get("source", "unknown")
        self.data["sources"][source] = self.data["sources"].get(source, 0) + 1
        category = article.get("category", "general")
        self.data["categories"][category] = self.data["categories"].get(category, 0) + 1
        self.data["total_read"] = self.data.get("total_read", 0) + 1
        self._save()

    def daily_average(self):
        """average articles read per day."""
        daily = self.data.get("daily", {})
        if not daily:
            return 0
        return round(sum(daily.values()) / len(daily), 1)

    def top_sources(self, n=5):
        """most read sources."""
        sources = self.data.get("sources", {})
        return sorted(sources.items(), key=lambda x: x[1], reverse=True)[:n]

    def top_categories(self, n=5):
        """most read categories."""
        cats = self.data.get("categories", {})
        return sorted(cats.items(), key=lambda x: x[1], reverse=True)[:n]

    def streak(self):
        """current reading streak in days."""
        import time
        daily = self.data.get("daily", {})
        if not daily:
            return 0
        today = time.strftime("%Y-%m-%d")
        count = 0
        current = today
        while current in daily:
            count += 1
            parts = current.split("-")
            from datetime import date, timedelta
            d = date(int(parts[0]), int(parts[1]), int(parts[2]))
            d -= timedelta(days=1)
            current = d.strftime("%Y-%m-%d")
        return count

    def summary(self):
        """generate reading summary."""
        return {
            "total_articles": self.data.get("total_read", 0),
            "daily_average": self.daily_average(),
            "days_tracked": len(self.data.get("daily", {})),
            "top_sources": self.top_sources(3),
            "top_categories": self.top_categories(3),
            "current_streak": self.streak(),
        }


if __name__ == "__main__":
    rs = ReadingStats("/tmp/newk_stats")
    rs.record({"source": "hackernews", "category": "tech"})
    rs.record({"source": "arxiv", "category": "science"})
    rs.record({"source": "hackernews", "category": "tech"})
    print(f"summary: {rs.summary()}")
