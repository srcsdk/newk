#!/usr/bin/env python3
"""merge multiple feeds into unified timeline"""

import hashlib


def merge_feeds(feeds):
    """merge multiple feed article lists into unified timeline."""
    seen = set()
    merged = []
    for feed in feeds:
        source = feed.get("source", "")
        for article in feed.get("articles", []):
            key = _dedup_key(article)
            if key in seen:
                continue
            seen.add(key)
            article["source"] = article.get("source", source)
            merged.append(article)
    merged.sort(key=lambda a: a.get("pub_date", a.get("date", "")), reverse=True)
    return merged


def _dedup_key(article):
    """generate deduplication key for article."""
    url = article.get("url", article.get("link", ""))
    if url:
        return hashlib.md5(url.encode()).hexdigest()
    title = article.get("title", "")
    return hashlib.md5(title.encode()).hexdigest()


def interleave_feeds(feeds, max_consecutive=3):
    """interleave articles from different feeds to avoid source clustering."""
    merged = merge_feeds(feeds)
    if not merged:
        return []
    result = []
    source_count = {}
    deferred = []
    for article in merged:
        source = article.get("source", "")
        count = source_count.get(source, 0)
        if count >= max_consecutive and deferred:
            inserted = False
            for i, d in enumerate(deferred):
                if d.get("source", "") != source:
                    result.append(deferred.pop(i))
                    source_count[d.get("source", "")] = 1
                    inserted = True
                    break
            if not inserted:
                result.extend(deferred)
                deferred.clear()
                source_count.clear()
        result.append(article)
        source_count[source] = source_count.get(source, 0) + 1
    result.extend(deferred)
    return result


if __name__ == "__main__":
    feeds = [
        {"source": "feed_a", "articles": [
            {"title": "a1", "date": "2022-01-03"},
            {"title": "a2", "date": "2022-01-01"},
        ]},
        {"source": "feed_b", "articles": [
            {"title": "b1", "date": "2022-01-02"},
            {"title": "b2", "date": "2022-01-04"},
        ]},
    ]
    merged = merge_feeds(feeds)
    print(f"merged: {len(merged)} articles")
    for a in merged:
        print(f"  {a['date']} [{a['source']}] {a['title']}")
