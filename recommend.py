#!/usr/bin/env python3
"""feed recommendation engine based on reading history"""

import json
import os
from collections import Counter


class Recommender:
    """recommend feeds based on user reading patterns."""

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.newk")
        self.data_dir = data_dir
        self.history_file = os.path.join(data_dir, "read_history.json")
        os.makedirs(data_dir, exist_ok=True)
        self.history = self._load()

    def _load(self):
        if os.path.isfile(self.history_file):
            with open(self.history_file) as f:
                return json.load(f)
        return {"reads": [], "likes": [], "topics": {}}

    def _save(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def record_read(self, article):
        """record that user read an article."""
        self.history["reads"].append({
            "title": article.get("title", ""),
            "source": article.get("source", ""),
            "category": article.get("category", ""),
        })
        cat = article.get("category", "general")
        self.history["topics"][cat] = self.history["topics"].get(cat, 0) + 1
        if len(self.history["reads"]) > 500:
            self.history["reads"] = self.history["reads"][-500:]
        self._save()

    def record_like(self, article):
        """record that user liked an article."""
        self.history["likes"].append({
            "title": article.get("title", ""),
            "source": article.get("source", ""),
            "category": article.get("category", ""),
        })
        self._save()

    def score_article(self, article):
        """score how relevant an article is to user interests."""
        score = 0
        cat = article.get("category", "")
        topic_counts = self.history.get("topics", {})
        total_reads = sum(topic_counts.values()) or 1
        if cat in topic_counts:
            score += topic_counts[cat] / total_reads * 50
        source = article.get("source", "")
        source_reads = sum(
            1 for r in self.history.get("reads", [])
            if r.get("source") == source
        )
        score += min(source_reads * 5, 30)
        liked_sources = Counter(
            r.get("source", "") for r in self.history.get("likes", [])
        )
        if source in liked_sources:
            score += liked_sources[source] * 10
        return min(score, 100)

    def rank_articles(self, articles):
        """rank articles by relevance score."""
        scored = [(self.score_article(a), a) for a in articles]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

    def top_topics(self, n=5):
        """get user's top topics."""
        topics = self.history.get("topics", {})
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        return sorted_topics[:n]


if __name__ == "__main__":
    rec = Recommender("/tmp/newk_rec")
    rec.record_read({"title": "python tips", "category": "programming", "source": "dev.to"})
    rec.record_read({"title": "rust guide", "category": "programming", "source": "rust-lang.org"})
    rec.record_read({"title": "ai news", "category": "technology", "source": "arxiv.org"})
    print(f"top topics: {rec.top_topics()}")
    test = {"title": "new python release", "category": "programming", "source": "dev.to"}
    print(f"score for python article: {rec.score_article(test)}")
