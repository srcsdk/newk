#!/usr/bin/env python3
"""arxiv category filters and citation count sorting"""

CATEGORIES = {
    "cs.AI": "artificial intelligence",
    "cs.LG": "machine learning",
    "cs.CR": "cryptography and security",
    "cs.SE": "software engineering",
    "cs.NE": "neural and evolutionary computing",
    "cs.CV": "computer vision",
    "cs.CL": "computation and language",
    "stat.ML": "machine learning (statistics)",
    "econ.EM": "econometrics",
    "q-bio": "quantitative biology",
    "physics": "physics",
}


def filter_by_category(articles, categories):
    """filter arxiv articles by category codes."""
    cat_set = set(categories)
    return [
        a for a in articles
        if any(c in cat_set for c in a.get("categories", []))
    ]


def sort_by_citations(articles, descending=True):
    """sort articles by citation count."""
    return sorted(
        articles,
        key=lambda a: a.get("citations", 0),
        reverse=descending,
    )


def extract_categories(category_string):
    """parse arxiv category string like 'cs.AI cs.LG stat.ML'."""
    return category_string.strip().split()


def score_relevance(article, keywords):
    """score article relevance based on keyword matches in title and abstract."""
    text = (article.get("title", "") + " " + article.get("abstract", "")).lower()
    matches = sum(1 for kw in keywords if kw.lower() in text)
    return matches / len(keywords) if keywords else 0


def top_papers(articles, categories=None, keywords=None, limit=20):
    """get top papers filtered by category and scored by relevance."""
    filtered = articles
    if categories:
        filtered = filter_by_category(filtered, categories)
    if keywords:
        for a in filtered:
            a["relevance"] = round(score_relevance(a, keywords), 3)
        filtered = sorted(filtered, key=lambda a: a["relevance"], reverse=True)
    return filtered[:limit]


if __name__ == "__main__":
    sample = [
        {"title": "deep learning for security", "categories": ["cs.CR", "cs.LG"],
         "citations": 45, "abstract": "neural network intrusion detection"},
        {"title": "reinforcement learning survey", "categories": ["cs.AI"],
         "citations": 120, "abstract": "survey of rl methods"},
        {"title": "market microstructure", "categories": ["econ.EM"],
         "citations": 30, "abstract": "high frequency trading analysis"},
    ]
    top = top_papers(sample, categories=["cs.CR", "cs.AI"], keywords=["security"])
    for p in top:
        print(f"  {p['title']} (citations: {p.get('citations', 0)})")
