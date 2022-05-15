#!/usr/bin/env python3
"""extractive text summarization for articles"""

import re
import math
from collections import Counter


def summarize(text, num_sentences=3):
    """extract most important sentences from text."""
    sentences = _split_sentences(text)
    if len(sentences) <= num_sentences:
        return text
    scores = _score_sentences(sentences)
    ranked = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)
    selected = sorted(ranked[:num_sentences])
    return " ".join(sentences[i] for i in selected)


def _split_sentences(text):
    """split text into sentences."""
    text = re.sub(r'\s+', ' ', text.strip())
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def _score_sentences(sentences):
    """score sentences by importance."""
    word_freq = Counter()
    for sent in sentences:
        words = re.findall(r'\b[a-z]+\b', sent.lower())
        word_freq.update(words)
    if not word_freq:
        return [0] * len(sentences)
    max_freq = max(word_freq.values())
    for word in word_freq:
        word_freq[word] /= max_freq
    scores = []
    for i, sent in enumerate(sentences):
        words = re.findall(r'\b[a-z]+\b', sent.lower())
        if not words:
            scores.append(0)
            continue
        score = sum(word_freq.get(w, 0) for w in words) / len(words)
        if i == 0:
            score *= 1.5
        if i < 3:
            score *= 1.2
        scores.append(score)
    return scores


def headline(text, max_length=80):
    """generate a short headline from text."""
    sentences = _split_sentences(text)
    if not sentences:
        return text[:max_length]
    first = sentences[0]
    if len(first) <= max_length:
        return first
    words = first.split()
    result = []
    length = 0
    for word in words:
        if length + len(word) + 1 > max_length:
            break
        result.append(word)
        length += len(word) + 1
    return " ".join(result) + "..."


if __name__ == "__main__":
    sample = (
        "Python 3.11 was released with significant speed improvements. "
        "The new version includes better error messages and exception groups. "
        "Performance benchmarks show up to 25% faster execution. "
        "The release also introduces the tomllib module for parsing TOML files. "
        "Developers can upgrade using pip or their package manager."
    )
    print(f"summary: {summarize(sample, 2)}")
    print(f"headline: {headline(sample)}")
