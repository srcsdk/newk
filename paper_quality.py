#!/usr/bin/env python3
"""research paper quality scoring with h-index weighting"""

import math


def h_index(citation_counts):
    """calculate h-index from list of citation counts."""
    sorted_counts = sorted(citation_counts, reverse=True)
    h = 0
    for i, count in enumerate(sorted_counts):
        if count >= i + 1:
            h = i + 1
        else:
            break
    return h


def journal_impact_score(journal_name, impact_factors=None):
    """lookup journal impact factor score (0-10 scale)."""
    if impact_factors is None:
        impact_factors = {
            "nature": 10, "science": 9.5, "cell": 9,
            "lancet": 8.5, "nejm": 9, "pnas": 7,
            "plos one": 4, "arxiv": 3,
        }
    name_lower = journal_name.lower()
    for journal, score in impact_factors.items():
        if journal in name_lower:
            return score
    return 3.0


def citation_velocity(citations, years_since_pub):
    """citations per year, weighted for recency."""
    if years_since_pub <= 0:
        return float(citations)
    return citations / years_since_pub


def author_score(author_citations):
    """score author credibility from their citation history."""
    if not author_citations:
        return 0
    h = h_index(author_citations)
    total = sum(author_citations)
    return min(10, h * 0.5 + math.log1p(total) * 0.3)


def quality_score(paper):
    """composite quality score for a research paper (0-100)."""
    journal = journal_impact_score(paper.get("journal", ""))
    citations = paper.get("citations", 0)
    years = max(1, paper.get("years_since_pub", 1))
    velocity = citation_velocity(citations, years)
    author = author_score(paper.get("author_citations", []))
    score = (
        journal * 3
        + min(10, velocity) * 3
        + author * 2
        + min(10, math.log1p(citations)) * 2
    )
    return round(min(100, score), 1)


if __name__ == "__main__":
    papers = [
        {"title": "deep learning review", "journal": "Nature", "citations": 5000,
         "years_since_pub": 5, "author_citations": [100, 80, 60, 40, 20]},
        {"title": "novel method", "journal": "PLOS ONE", "citations": 15,
         "years_since_pub": 1, "author_citations": [10, 5, 3]},
    ]
    for p in papers:
        score = quality_score(p)
        print(f"  {p['title']}: quality={score}")
