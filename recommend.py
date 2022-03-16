#!/usr/bin/env python3
"""content recommendation based on reading history"""

from collections import defaultdict


def build_profile(history, decay=0.95):
    """build user interest profile from reading history.

    more recent reads are weighted higher.
    """
    scores = defaultdict(float)
    weight = 1.0
    for item in reversed(history):
        for tag in item.get("tags", []):
            scores[tag] += weight
        category = item.get("category", "")
        if category:
            scores[category] += weight * 1.5
        weight *= decay
    total = sum(scores.values()) or 1
    return {k: round(v / total, 4) for k, v in scores.items()}


def score_article(article, profile):
    """score an article against user profile."""
    score = 0
    for tag in article.get("tags", []):
        score += profile.get(tag, 0)
    category = article.get("category", "")
    if category:
        score += profile.get(category, 0) * 2
    quality = article.get("quality_score", 0.5)
    score *= (0.5 + quality)
    return round(score, 4)


def recommend(articles, profile, n=10, seen=None):
    """return top n recommended articles."""
    if seen is None:
        seen = set()
    candidates = [a for a in articles if a.get("id") not in seen]
    scored = [(a, score_article(a, profile)) for a in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [a for a, s in scored[:n]]


def diversity_boost(recommendations, max_per_category=3):
    """limit articles per category to increase diversity."""
    counts = defaultdict(int)
    diverse = []
    for article in recommendations:
        cat = article.get("category", "other")
        if counts[cat] < max_per_category:
            diverse.append(article)
            counts[cat] += 1
    return diverse


def cold_start_recommendations(articles, n=10):
    """recommendations for new users based on popularity."""
    sorted_articles = sorted(
        articles,
        key=lambda a: a.get("popularity", 0),
        reverse=True,
    )
    return sorted_articles[:n]


if __name__ == "__main__":
    history = [
        {"tags": ["python", "tutorial"], "category": "programming"},
        {"tags": ["linux", "security"], "category": "technology"},
        {"tags": ["python", "data"], "category": "programming"},
    ]
    profile = build_profile(history)
    print("user profile:")
    for k, v in sorted(profile.items(), key=lambda x: x[1], reverse=True):
        print(f"  {k}: {v}")
    articles = [
        {"id": 1, "tags": ["python", "web"], "category": "programming",
         "quality_score": 0.8},
        {"id": 2, "tags": ["sports"], "category": "entertainment",
         "quality_score": 0.9},
        {"id": 3, "tags": ["linux", "kernel"], "category": "technology",
         "quality_score": 0.7},
    ]
    recs = recommend(articles, profile, n=3)
    for r in recs:
        print(f"  recommended: {r['tags']}")
