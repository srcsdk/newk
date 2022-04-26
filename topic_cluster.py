#!/usr/bin/env python3
"""cluster articles by topic similarity"""

import re
import math
from collections import Counter


def extract_keywords(text, min_length=3):
    """extract significant keywords from text."""
    stop_words = {
        "the", "and", "for", "that", "this", "with", "from", "are", "was",
        "were", "been", "have", "has", "had", "will", "would", "could",
        "should", "may", "might", "can", "not", "but", "its", "all",
        "more", "some", "than", "other", "into", "also", "just", "about",
        "over", "such", "after", "before", "between", "each", "which",
        "their", "there", "these", "those", "what", "when", "where",
        "who", "how", "our", "your", "out", "new", "one", "two",
    }
    words = re.findall(r'\b[a-z]{%d,}\b' % min_length, text.lower())
    return [w for w in words if w not in stop_words]


def tfidf_vectors(documents):
    """compute tf-idf vectors for documents."""
    doc_freq = Counter()
    doc_terms = []
    for doc in documents:
        terms = Counter(extract_keywords(doc.get("title", "") + " " + doc.get("description", "")))
        doc_terms.append(terms)
        for term in terms:
            doc_freq[term] += 1
    n_docs = len(documents)
    vectors = []
    for terms in doc_terms:
        vec = {}
        for term, count in terms.items():
            tf = count / max(sum(terms.values()), 1)
            idf = math.log(n_docs / max(doc_freq[term], 1))
            vec[term] = tf * idf
        vectors.append(vec)
    return vectors


def cosine_similarity(vec_a, vec_b):
    """compute cosine similarity between two sparse vectors."""
    common = set(vec_a.keys()) & set(vec_b.keys())
    if not common:
        return 0
    dot = sum(vec_a[k] * vec_b[k] for k in common)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0
    return dot / (mag_a * mag_b)


def cluster_articles(articles, threshold=0.15):
    """cluster articles by topic similarity."""
    if not articles:
        return []
    vectors = tfidf_vectors(articles)
    clusters = []
    assigned = set()
    for i in range(len(articles)):
        if i in assigned:
            continue
        cluster = [i]
        assigned.add(i)
        for j in range(i + 1, len(articles)):
            if j in assigned:
                continue
            sim = cosine_similarity(vectors[i], vectors[j])
            if sim >= threshold:
                cluster.append(j)
                assigned.add(j)
        topic_words = _cluster_keywords(cluster, vectors)
        clusters.append({
            "articles": [articles[idx] for idx in cluster],
            "size": len(cluster),
            "topic": " ".join(topic_words[:3]),
        })
    clusters.sort(key=lambda c: c["size"], reverse=True)
    return clusters


def _cluster_keywords(indices, vectors):
    """find top keywords for a cluster."""
    combined = Counter()
    for idx in indices:
        for term, score in vectors[idx].items():
            combined[term] += score
    return [term for term, _ in combined.most_common(5)]


if __name__ == "__main__":
    articles = [
        {"title": "python 3.11 released", "description": "new python version with speed improvements"},
        {"title": "python type hints guide", "description": "how to use type annotations in python"},
        {"title": "rust memory safety", "description": "understanding ownership and borrowing in rust"},
        {"title": "rust async programming", "description": "async await patterns in rust language"},
    ]
    clusters = cluster_articles(articles)
    print(f"clusters: {len(clusters)}")
    for cl in clusters:
        print(f"  topic: {cl['topic']} ({cl['size']} articles)")
        for a in cl["articles"]:
            print(f"    - {a['title']}")
