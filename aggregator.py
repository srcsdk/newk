#!/usr/bin/env python3
"""multi-source feed aggregation with deduplication"""

import hashlib
import re
from collections import defaultdict


def normalize_title(title):
    """normalize title for dedup comparison."""
    title = title.lower().strip()
    title = re.sub(r"[^a-z0-9\s]", "", title)
    title = re.sub(r"\s+", " ", title)
    return title


def title_hash(title):
    """generate hash of normalized title."""
    return hashlib.md5(normalize_title(title).encode()).hexdigest()[:12]


def deduplicate(articles):
    """remove duplicate articles based on title similarity."""
    seen = {}
    unique = []
    for article in articles:
        h = title_hash(article.get("title", ""))
        if h not in seen:
            seen[h] = True
            unique.append(article)
    return unique


def merge_sources(feeds):
    """merge articles from multiple feed sources.

    feeds: dict of {source_name: [articles]}
    returns deduplicated list sorted by date.
    """
    all_articles = []
    for source, articles in feeds.items():
        for article in articles:
            article["source"] = source
            all_articles.append(article)
    deduped = deduplicate(all_articles)
    deduped.sort(key=lambda a: a.get("date", ""), reverse=True)
    return deduped


def group_by_topic(articles):
    """group articles by shared keywords."""
    groups = defaultdict(list)
    for article in articles:
        tags = article.get("tags", [])
        if tags:
            key = tags[0] if tags else "uncategorized"
            groups[key].append(article)
        else:
            groups["uncategorized"].append(article)
    return dict(groups)


def source_diversity(articles):
    """measure how many different sources are represented."""
    sources = set(a.get("source", "") for a in articles)
    return {
        "total_sources": len(sources),
        "sources": sorted(sources),
        "articles_per_source": {
            s: sum(1 for a in articles if a.get("source") == s)
            for s in sources
        },
    }


if __name__ == "__main__":
    feeds = {
        "arxiv": [
            {"title": "Deep Learning Survey", "date": "2021-10-01", "tags": ["ml"]},
            {"title": "Neural Network Optimization", "date": "2021-10-02", "tags": ["ml"]},
        ],
        "pubmed": [
            {"title": "deep learning survey", "date": "2021-10-01", "tags": ["ml"]},
            {"title": "Vaccine Efficacy Study", "date": "2021-10-03", "tags": ["health"]},
        ],
    }
    merged = merge_sources(feeds)
    print(f"total after dedup: {len(merged)}")
    diversity = source_diversity(merged)
    print(f"sources: {diversity['total_sources']}")
