#!/usr/bin/env python3
"""article summarization - extract key sentences from content"""

import re
from collections import Counter


def clean_html(text):
    """strip html tags and decode entities"""
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_sentences(text):
    """split text into sentences"""
    text = clean_html(text)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def word_frequencies(text):
    """calculate word frequencies, ignoring common stop words"""
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "could", "should", "may", "might", "can", "shall",
        "this", "that", "these", "those", "it", "its", "they", "them",
        "their", "we", "our", "he", "she", "his", "her", "not", "no",
        "if", "then", "than", "so", "as", "also", "just", "about",
    }
    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    filtered = [w for w in words if w not in stop_words]
    return Counter(filtered)


def score_sentence(sentence, freq, position, total_sentences):
    """score a sentence based on word importance and position"""
    words = re.findall(r"\b[a-z]{3,}\b", sentence.lower())
    if not words:
        return 0

    # word frequency score
    word_score = sum(freq.get(w, 0) for w in words) / len(words)

    # position bonus (first and last sentences are often important)
    pos_ratio = position / max(total_sentences, 1)
    pos_score = 1.0
    if pos_ratio < 0.2:
        pos_score = 1.5
    elif pos_ratio > 0.8:
        pos_score = 1.2

    # length bonus (medium length sentences preferred)
    length = len(words)
    length_score = 1.0
    if 10 <= length <= 25:
        length_score = 1.2
    elif length > 40:
        length_score = 0.8

    return word_score * pos_score * length_score


def summarize(text, num_sentences=3):
    """extract the most important sentences as a summary"""
    sentences = split_sentences(text)
    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    freq = word_frequencies(text)
    scored = []
    for i, sent in enumerate(sentences):
        score = score_sentence(sent, freq, i, len(sentences))
        scored.append((i, score, sent))

    # sort by score, take top n, then reorder by position
    top = sorted(scored, key=lambda x: x[1], reverse=True)[:num_sentences]
    top.sort(key=lambda x: x[0])

    return " ".join(s[2] for s in top)


def extract_keywords(text, top_n=10):
    """extract top keywords from text"""
    freq = word_frequencies(text)
    return [word for word, _ in freq.most_common(top_n)]


def summarize_article(article, num_sentences=3):
    """summarize an article dict (uses description/abstract field)"""
    content = article.get("description", article.get("abstract", ""))
    if not content:
        return article.get("title", "")

    summary = summarize(content, num_sentences)
    keywords = extract_keywords(content, 5)

    return {
        "title": article.get("title", ""),
        "summary": summary,
        "keywords": keywords,
        "original_length": len(content),
        "summary_length": len(summary),
    }
