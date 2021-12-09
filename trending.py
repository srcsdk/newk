#!/usr/bin/env python3
"""trending topics detection across feed sources"""

import re
from collections import Counter


STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "and", "but", "or", "nor", "not", "so", "yet",
    "this", "that", "these", "those", "it", "its", "they", "them",
    "their", "we", "our", "you", "your", "he", "she", "his", "her",
}


def extract_keywords(text, min_length=3):
    """extract meaningful keywords from text."""
    words = re.findall(r"[a-z]+", text.lower())
    return [w for w in words if len(w) >= min_length and w not in STOP_WORDS]


def keyword_frequency(articles, field="title"):
    """count keyword frequency across articles."""
    counter = Counter()
    for article in articles:
        keywords = extract_keywords(article.get(field, ""))
        counter.update(keywords)
    return counter


def detect_trending(articles, window_articles=None, threshold=2.0):
    """detect trending topics by comparing recent vs baseline frequency.

    threshold: minimum ratio of recent/baseline frequency to be trending.
    """
    if window_articles is None:
        split = len(articles) // 2
        window_articles = articles[:split]
        articles = articles[split:]
    baseline = keyword_frequency(window_articles)
    current = keyword_frequency(articles)
    trending = []
    for word, count in current.most_common(100):
        base_count = baseline.get(word, 1)
        ratio = count / base_count
        if ratio >= threshold and count >= 3:
            trending.append({
                "keyword": word,
                "current_count": count,
                "baseline_count": base_count,
                "velocity": round(ratio, 2),
            })
    trending.sort(key=lambda t: t["velocity"], reverse=True)
    return trending


def burst_detection(keyword_counts_over_time, threshold=3.0):
    """detect keyword bursts using simple deviation from mean."""
    if len(keyword_counts_over_time) < 5:
        return False
    mean = sum(keyword_counts_over_time) / len(keyword_counts_over_time)
    if mean == 0:
        return False
    latest = keyword_counts_over_time[-1]
    return latest / mean >= threshold


if __name__ == "__main__":
    articles = [
        {"title": "New AI model achieves state of the art results"},
        {"title": "AI safety research gains momentum"},
        {"title": "Quantum computing breakthrough reported"},
        {"title": "AI regulation debate continues in congress"},
    ]
    trending = detect_trending(articles)
    print("trending topics:")
    for t in trending[:10]:
        print(f"  {t['keyword']}: velocity={t['velocity']}x")
