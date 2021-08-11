#!/usr/bin/env python3
"""feed deduplication to remove duplicate articles across sources"""

import hashlib
import re


def normalize_text(text):
    """normalize text for comparison"""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def title_hash(title):
    """generate a hash from normalized title"""
    normalized = normalize_text(title)
    return hashlib.md5(normalized.encode()).hexdigest()


def link_hash(link):
    """generate a hash from a url, ignoring query params and fragments"""
    # strip protocol, trailing slashes, and common tracking params
    cleaned = re.sub(r"^https?://", "", link)
    cleaned = re.sub(r"[?#].*$", "", cleaned)
    cleaned = cleaned.rstrip("/")
    return hashlib.md5(cleaned.encode()).hexdigest()


def similarity_score(text_a, text_b):
    """calculate simple word overlap similarity between two texts"""
    words_a = set(normalize_text(text_a).split())
    words_b = set(normalize_text(text_b).split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def deduplicate(articles, threshold=0.7):
    """remove duplicate articles from a list.

    uses title hashing for exact matches and similarity scoring
    for near-duplicates. keeps the first occurrence.
    """
    seen_titles = {}
    seen_links = set()
    unique = []

    for article in articles:
        title = article.get("title", "")
        link = article.get("link", "")

        # skip if exact link match
        lhash = link_hash(link) if link else None
        if lhash and lhash in seen_links:
            continue

        # skip if exact title match
        thash = title_hash(title)
        if thash in seen_titles:
            continue

        # check similarity against recent titles
        is_dup = False
        for seen_title in list(seen_titles.values())[-50:]:
            if similarity_score(title, seen_title) >= threshold:
                is_dup = True
                break

        if is_dup:
            continue

        seen_titles[thash] = title
        if lhash:
            seen_links.add(lhash)
        unique.append(article)

    return unique


def merge_feeds(feed_lists, threshold=0.7):
    """merge multiple feed lists and deduplicate"""
    all_articles = []
    for feed in feed_lists:
        all_articles.extend(feed)
    return deduplicate(all_articles, threshold)


def dedup_stats(original_count, deduped_count):
    """return deduplication statistics"""
    removed = original_count - deduped_count
    pct = (removed / max(original_count, 1)) * 100
    return {
        "original": original_count,
        "unique": deduped_count,
        "duplicates_removed": removed,
        "reduction_pct": round(pct, 1),
    }
