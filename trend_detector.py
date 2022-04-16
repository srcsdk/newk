#!/usr/bin/env python3
"""detect trending topics across news feeds"""

import re
from collections import defaultdict


def extract_keywords(text, min_length=3):
    """extract meaningful keywords from text."""
    stop_words = {
        "the", "and", "for", "are", "but", "not", "you", "all",
        "can", "had", "her", "was", "one", "our", "out", "has",
        "its", "his", "how", "man", "new", "now", "old", "see",
        "way", "who", "did", "get", "let", "say", "she", "too",
        "use", "been", "have", "from", "this", "that", "with",
        "they", "will", "what", "when", "make", "like", "just",
        "than", "them", "been", "some", "then", "into", "also",
    }
    words = re.findall(r"\b[a-z]+\b", text.lower())
    return [w for w in words if len(w) >= min_length and w not in stop_words]


def keyword_frequency(articles, field="title"):
    """count keyword frequency across articles."""
    freq = defaultdict(int)
    for article in articles:
        text = article.get(field, "")
        keywords = extract_keywords(text)
        seen = set()
        for kw in keywords:
            if kw not in seen:
                freq[kw] += 1
                seen.add(kw)
    return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))


def detect_trends(articles, window_hours=24, min_mentions=3):
    """detect trending topics from recent articles."""
    freq = keyword_frequency(articles)
    trends = []
    for keyword, count in freq.items():
        if count >= min_mentions:
            trends.append({
                "keyword": keyword,
                "mentions": count,
                "score": round(count / len(articles) * 100, 2),
            })
    trends.sort(key=lambda t: t["score"], reverse=True)
    return trends


def trend_velocity(current_freq, previous_freq):
    """calculate how fast topics are trending up or down."""
    velocity = {}
    all_keywords = set(list(current_freq.keys()) + list(previous_freq.keys()))
    for kw in all_keywords:
        curr = current_freq.get(kw, 0)
        prev = previous_freq.get(kw, 0)
        if prev > 0:
            change = (curr - prev) / prev
        elif curr > 0:
            change = 1.0
        else:
            change = 0
        if abs(change) > 0.1:
            velocity[kw] = round(change, 2)
    return dict(sorted(velocity.items(), key=lambda x: x[1], reverse=True))


def categorize_trend(keyword, category_keywords):
    """assign a trend to a category."""
    for category, keywords in category_keywords.items():
        if keyword in keywords:
            return category
    return "general"


if __name__ == "__main__":
    articles = [
        {"title": "python 3.11 brings major performance improvements"},
        {"title": "new python framework challenges django and flask"},
        {"title": "rust adoption growing among python developers"},
        {"title": "machine learning with python reaches new milestone"},
        {"title": "linux kernel 5.17 released with performance fixes"},
        {"title": "open source projects see record contributions"},
    ]
    trends = detect_trends(articles, min_mentions=2)
    print("trending topics:")
    for t in trends[:10]:
        print(f"  {t['keyword']}: {t['mentions']} mentions ({t['score']}%)")
