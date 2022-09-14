#!/usr/bin/env python3
"""quality filtering for research and data feeds"""

import re
from collections import Counter


class QualityFilter:
    """filter feed items by content quality signals."""

    def __init__(self, min_score=0.3):
        self.min_score = min_score
        self.blocked_domains = set()
        self.trusted_domains = set()

    def score(self, item):
        """score a feed item for quality."""
        scores = []
        scores.append(self._source_score(item))
        scores.append(self._content_score(item))
        scores.append(self._freshness_score(item))
        scores.append(self._relevance_score(item))
        weights = [0.3, 0.3, 0.2, 0.2]
        total = sum(s * w for s, w in zip(scores, weights))
        return round(total, 3)

    def _source_score(self, item):
        """score based on source reputation."""
        domain = item.get("domain", "")
        if domain in self.blocked_domains:
            return 0
        if domain in self.trusted_domains:
            return 1.0
        academic = [".edu", ".gov", "arxiv", "pubmed", "nature.com"]
        if any(a in domain for a in academic):
            return 0.9
        return 0.5

    def _content_score(self, item):
        """score based on content quality signals."""
        text = item.get("text", "") or item.get("summary", "")
        if not text:
            return 0.1
        word_count = len(text.split())
        if word_count < 50:
            return 0.2
        elif word_count < 200:
            return 0.5
        elif word_count < 1000:
            return 0.8
        return 0.7

    def _freshness_score(self, item):
        """score based on recency."""
        age_hours = item.get("age_hours", 0)
        if age_hours < 1:
            return 1.0
        elif age_hours < 24:
            return 0.8
        elif age_hours < 72:
            return 0.5
        elif age_hours < 168:
            return 0.3
        return 0.1

    def _relevance_score(self, item):
        """score based on keyword relevance."""
        keywords = item.get("keywords", [])
        if not keywords:
            return 0.5
        return min(1.0, len(keywords) * 0.15)

    def filter(self, items):
        """filter items above quality threshold."""
        scored = [(item, self.score(item)) for item in items]
        return [
            {**item, "_quality": score}
            for item, score in scored
            if score >= self.min_score
        ]

    def add_trusted(self, domain):
        """add a trusted domain."""
        self.trusted_domains.add(domain)

    def add_blocked(self, domain):
        """block a low-quality domain."""
        self.blocked_domains.add(domain)

    def detect_duplicates(self, items, threshold=0.8):
        """detect near-duplicate items by title similarity."""
        seen = []
        unique = []
        for item in items:
            title = item.get("title", "").lower()
            words = set(re.findall(r'\w+', title))
            is_dup = False
            for seen_words in seen:
                if not words or not seen_words:
                    continue
                overlap = len(words & seen_words) / max(
                    len(words | seen_words), 1
                )
                if overlap >= threshold:
                    is_dup = True
                    break
            if not is_dup:
                unique.append(item)
                seen.append(words)
        return unique


if __name__ == "__main__":
    qf = QualityFilter(min_score=0.4)
    qf.add_trusted("arxiv.org")
    items = [
        {"title": "new ml paper", "domain": "arxiv.org",
         "text": "a " * 200, "age_hours": 2},
        {"title": "clickbait", "domain": "spam.com",
         "text": "short", "age_hours": 48},
    ]
    filtered = qf.filter(items)
    print(f"filtered: {len(filtered)}/{len(items)} items passed")
