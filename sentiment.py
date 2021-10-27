#!/usr/bin/env python3
"""sentiment analysis for article headlines"""

import re

POSITIVE_WORDS = {
    "breakthrough", "success", "improve", "advance", "growth", "gain",
    "benefit", "effective", "promising", "innovative", "discover",
    "achieve", "progress", "positive", "strong", "boost", "win",
}

NEGATIVE_WORDS = {
    "fail", "crisis", "decline", "risk", "loss", "threat", "concern",
    "warning", "collapse", "danger", "problem", "drop", "crash",
    "weak", "fear", "damage", "negative", "worse", "struggle",
}

INTENSIFIERS = {"very", "extremely", "highly", "significantly", "major"}
NEGATORS = {"not", "no", "never", "neither", "hardly", "barely"}


def tokenize(text):
    """simple word tokenization."""
    return re.findall(r"[a-z]+", text.lower())


def sentiment_score(text):
    """calculate sentiment score from -1 (negative) to 1 (positive)."""
    words = tokenize(text)
    if not words:
        return 0.0
    pos = sum(1 for w in words if w in POSITIVE_WORDS)
    neg = sum(1 for w in words if w in NEGATIVE_WORDS)
    intensified = sum(1 for i, w in enumerate(words)
                      if i > 0 and words[i - 1] in INTENSIFIERS
                      and (w in POSITIVE_WORDS or w in NEGATIVE_WORDS))
    negated = sum(1 for i, w in enumerate(words)
                  if i > 0 and words[i - 1] in NEGATORS
                  and w in POSITIVE_WORDS)
    score = (pos - neg + intensified * 0.5 - negated * 2) / len(words)
    return max(-1.0, min(1.0, round(score, 3)))


def classify(score):
    """classify sentiment score into category."""
    if score > 0.1:
        return "positive"
    elif score < -0.1:
        return "negative"
    return "neutral"


def batch_sentiment(headlines):
    """analyze sentiment for a batch of headlines."""
    results = []
    for headline in headlines:
        score = sentiment_score(headline)
        results.append({
            "headline": headline,
            "score": score,
            "sentiment": classify(score),
        })
    return results


def aggregate_mood(headlines):
    """calculate overall mood from multiple headlines."""
    scores = [sentiment_score(h) for h in headlines]
    if not scores:
        return {"mood": "neutral", "avg_score": 0}
    avg = sum(scores) / len(scores)
    return {
        "mood": classify(avg),
        "avg_score": round(avg, 3),
        "positive_pct": round(sum(1 for s in scores if s > 0.1) / len(scores) * 100, 1),
        "negative_pct": round(sum(1 for s in scores if s < -0.1) / len(scores) * 100, 1),
    }


if __name__ == "__main__":
    headlines = [
        "Major breakthrough in quantum computing research",
        "Market crash fears grow as inflation concerns rise",
        "New study shows promising results for treatment",
        "Supply chain crisis threatens global growth",
    ]
    for result in batch_sentiment(headlines):
        print(f"  [{result['sentiment']:>8}] {result['score']:+.3f} {result['headline']}")
    print(f"  mood: {aggregate_mood(headlines)}")
