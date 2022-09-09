#!/usr/bin/env python3
"""generate daily/weekly digest of top articles"""

import time


class DigestGenerator:
    """generate article digests."""

    def __init__(self, articles=None):
        self.articles = articles or []

    def daily_digest(self, date=None):
        """generate daily digest of top articles."""
        if date is None:
            date = time.strftime("%Y-%m-%d")
        today_articles = [
            a for a in self.articles
            if a.get("date", "").startswith(date)
        ]
        if not today_articles:
            today_articles = self.articles
        scored = self._score_articles(today_articles)
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:10]
        digest = {
            "date": date,
            "article_count": len(top),
            "articles": [a for _, a in top],
        }
        return digest

    def weekly_digest(self):
        """generate weekly digest grouping by category."""
        categories = {}
        for article in self.articles:
            cat = article.get("category", "general")
            categories.setdefault(cat, []).append(article)
        digest = {"categories": {}}
        for cat, articles in categories.items():
            scored = self._score_articles(articles)
            scored.sort(key=lambda x: x[0], reverse=True)
            digest["categories"][cat] = [a for _, a in scored[:5]]
        return digest

    def _score_articles(self, articles):
        """score articles for ranking in digest."""
        scored = []
        for article in articles:
            score = 0
            score += article.get("likes", 0) * 2
            score += article.get("comments", 0) * 3
            score += article.get("shares", 0) * 5
            if article.get("title"):
                score += 1
            scored.append((score, article))
        return scored

    def format_text(self, digest):
        """format digest as plain text."""
        lines = [f"digest for {digest.get('date', 'this week')}", ""]
        articles = digest.get("articles", [])
        if articles:
            for i, a in enumerate(articles, 1):
                lines.append(f"{i}. {a.get('title', 'untitled')}")
                if a.get("source"):
                    lines.append(f"   source: {a['source']}")
                lines.append("")
        categories = digest.get("categories", {})
        for cat, cat_articles in categories.items():
            lines.append(f"[{cat}]")
            for a in cat_articles:
                lines.append(f"  - {a.get('title', 'untitled')}")
            lines.append("")
        return "\n".join(lines)


if __name__ == "__main__":
    articles = [
        {"title": "article one", "category": "tech", "likes": 100, "date": time.strftime("%Y-%m-%d")},
        {"title": "article two", "category": "science", "likes": 50, "date": time.strftime("%Y-%m-%d")},
        {"title": "article three", "category": "tech", "likes": 200, "date": time.strftime("%Y-%m-%d")},
    ]
    dg = DigestGenerator(articles)
    daily = dg.daily_digest()
    print(dg.format_text(daily))
