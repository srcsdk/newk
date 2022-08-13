#!/usr/bin/env python3
"""advanced content filtering for feeds"""

import re


class ContentFilter:
    """filter articles based on rules."""

    def __init__(self):
        self.rules = []

    def add_keyword_rule(self, keyword, action="include"):
        """add keyword-based filter rule."""
        self.rules.append({
            "type": "keyword",
            "keyword": keyword.lower(),
            "action": action,
        })

    def add_source_rule(self, source, action="include"):
        """add source-based filter rule."""
        self.rules.append({
            "type": "source",
            "source": source.lower(),
            "action": action,
        })

    def add_length_rule(self, min_words=0, max_words=0):
        """add content length filter."""
        self.rules.append({
            "type": "length",
            "min_words": min_words,
            "max_words": max_words,
        })

    def add_regex_rule(self, pattern, action="include"):
        """add regex-based filter rule."""
        self.rules.append({
            "type": "regex",
            "pattern": pattern,
            "action": action,
        })

    def apply(self, articles):
        """apply all filter rules to articles."""
        filtered = []
        for article in articles:
            if self._passes(article):
                filtered.append(article)
        return filtered

    def _passes(self, article):
        """check if article passes all rules."""
        text = (article.get("title", "") + " " + article.get("description", "")).lower()
        source = article.get("source", "").lower()
        for rule in self.rules:
            if rule["type"] == "keyword":
                found = rule["keyword"] in text
                if rule["action"] == "exclude" and found:
                    return False
                if rule["action"] == "include" and not found:
                    return False
            elif rule["type"] == "source":
                matches = rule["source"] in source
                if rule["action"] == "exclude" and matches:
                    return False
            elif rule["type"] == "length":
                words = len(text.split())
                if rule["min_words"] and words < rule["min_words"]:
                    return False
                if rule["max_words"] and words > rule["max_words"]:
                    return False
            elif rule["type"] == "regex":
                found = bool(re.search(rule["pattern"], text))
                if rule["action"] == "exclude" and found:
                    return False
                if rule["action"] == "include" and not found:
                    return False
        return True


if __name__ == "__main__":
    cf = ContentFilter()
    cf.add_keyword_rule("spam", "exclude")
    cf.add_length_rule(min_words=5)
    articles = [
        {"title": "good article about python", "description": "python programming tips"},
        {"title": "spam offer", "description": "buy now spam deal"},
        {"title": "short", "description": ""},
        {"title": "rust programming guide", "description": "learn rust language basics"},
    ]
    filtered = cf.apply(articles)
    print(f"filtered: {len(filtered)}/{len(articles)}")
    for a in filtered:
        print(f"  {a['title']}")
