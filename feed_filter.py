#!/usr/bin/env python3
"""keyword and quality filters for feed articles"""

import re


def keyword_filter(articles, include=None, exclude=None):
    """filter articles by keyword inclusion/exclusion.

    checks title and summary fields.
    """
    filtered = []
    for article in articles:
        text = (article.get("title", "") + " " + article.get("summary", "")).lower()
        if exclude:
            if any(kw.lower() in text for kw in exclude):
                continue
        if include:
            if not any(kw.lower() in text for kw in include):
                continue
        filtered.append(article)
    return filtered


def quality_score(article):
    """score article quality based on content indicators."""
    score = 0
    title = article.get("title", "")
    summary = article.get("summary", "")
    if len(title) > 10:
        score += 1
    if len(title) > 30:
        score += 1
    if len(summary) > 100:
        score += 2
    if len(summary) > 500:
        score += 1
    if article.get("author"):
        score += 1
    if article.get("doi") or article.get("arxiv_id"):
        score += 3
    clickbait = ["you wont believe", "shocking", "this one trick", "gone wrong"]
    if any(cb in title.lower() for cb in clickbait):
        score -= 3
    return max(0, score)


def filter_by_quality(articles, min_score=3):
    """keep only articles meeting minimum quality score."""
    return [a for a in articles if quality_score(a) >= min_score]


def deduplicate(articles, key="title"):
    """remove duplicate articles by normalized key."""
    seen = set()
    unique = []
    for article in articles:
        normalized = re.sub(r"\s+", " ", article.get(key, "").lower().strip())
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique.append(article)
    return unique


def filter_by_date(articles, after=None, before=None, date_key="published"):
    """filter articles by date range."""
    filtered = []
    for article in articles:
        d = article.get(date_key, "")
        if after and d < after:
            continue
        if before and d > before:
            continue
        filtered.append(article)
    return filtered


if __name__ == "__main__":
    articles = [
        {"title": "machine learning advances in genomics", "summary": "a " * 100, "author": "smith"},
        {"title": "you wont believe this trick", "summary": "click here"},
        {"title": "arxiv: deep reinforcement learning", "summary": "we present...", "arxiv_id": "2201.12345"},
    ]
    scored = [(a["title"][:40], quality_score(a)) for a in articles]
    for title, score in scored:
        print(f"  {score}: {title}")
    filtered = filter_by_quality(articles, min_score=3)
    print(f"passed quality filter: {len(filtered)}/{len(articles)}")
