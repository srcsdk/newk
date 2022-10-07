#!/usr/bin/env python3
"""track keywords across feeds over time"""

import json
import os
import time
from collections import Counter
import re


class KeywordTracker:
    """track keyword frequency across feed articles."""

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.newk")
        self.data_dir = data_dir
        self.data_file = os.path.join(data_dir, "keywords.json")
        os.makedirs(data_dir, exist_ok=True)
        self.data = self._load()

    def _load(self):
        if os.path.isfile(self.data_file):
            with open(self.data_file) as f:
                return json.load(f)
        return {"tracked": [], "history": {}}

    def _save(self):
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def track(self, keyword):
        """add a keyword to track."""
        keyword = keyword.lower()
        if keyword not in self.data["tracked"]:
            self.data["tracked"].append(keyword)
            self._save()

    def untrack(self, keyword):
        """stop tracking a keyword."""
        keyword = keyword.lower()
        if keyword in self.data["tracked"]:
            self.data["tracked"].remove(keyword)
            self._save()

    def scan_articles(self, articles):
        """scan articles for tracked keywords."""
        date = time.strftime("%Y-%m-%d")
        counts = Counter()
        matches = []
        for article in articles:
            text = (article.get("title", "") + " " + article.get("description", "")).lower()
            for kw in self.data["tracked"]:
                if kw in text:
                    count = len(re.findall(re.escape(kw), text))
                    counts[kw] += count
                    matches.append({"keyword": kw, "article": article.get("title", "")})
        if date not in self.data["history"]:
            self.data["history"][date] = {}
        for kw, count in counts.items():
            prev = self.data["history"][date].get(kw, 0)
            self.data["history"][date][kw] = prev + count
        self._save()
        return matches

    def trend(self, keyword, days=7):
        """get keyword frequency trend over recent days."""
        keyword = keyword.lower()
        history = self.data.get("history", {})
        dates = sorted(history.keys(), reverse=True)[:days]
        return [
            {"date": d, "count": history[d].get(keyword, 0)}
            for d in reversed(dates)
        ]

    def top_keywords(self, n=10):
        """get most frequently seen tracked keywords."""
        totals = Counter()
        for day_data in self.data.get("history", {}).values():
            for kw, count in day_data.items():
                totals[kw] += count
        return totals.most_common(n)


if __name__ == "__main__":
    kt = KeywordTracker("/tmp/newk_kw")
    kt.track("python")
    kt.track("rust")
    kt.track("linux")
    articles = [
        {"title": "python 3.11 performance", "description": "python speed improvements"},
        {"title": "rust async guide", "description": "learn async rust programming"},
        {"title": "linux kernel update", "description": "new linux kernel release"},
    ]
    matches = kt.scan_articles(articles)
    print(f"matches: {len(matches)}")
    for m in matches:
        print(f"  [{m['keyword']}] {m['article']}")
