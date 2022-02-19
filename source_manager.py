#!/usr/bin/env python3
"""feed source priority and refresh frequency settings"""

import json
import os


SOURCE_CONFIG_FILE = os.path.expanduser("~/.config/newk/sources.json")

DEFAULT_SOURCES = {
    "arxiv": {"url": "http://arxiv.org/rss/cs", "priority": 1, "refresh_min": 60},
    "pubmed": {"url": "https://pubmed.ncbi.nlm.nih.gov/rss/", "priority": 1, "refresh_min": 120},
    "hackernews": {"url": "https://news.ycombinator.com/rss", "priority": 2, "refresh_min": 30},
}


def load_sources():
    """load source configuration from file."""
    if os.path.exists(SOURCE_CONFIG_FILE):
        with open(SOURCE_CONFIG_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_SOURCES.copy()


def save_sources(sources):
    """save source configuration to file."""
    os.makedirs(os.path.dirname(SOURCE_CONFIG_FILE), exist_ok=True)
    with open(SOURCE_CONFIG_FILE, "w") as f:
        json.dump(sources, f, indent=2)


def add_source(name, url, priority=3, refresh_min=60):
    """add a new feed source."""
    sources = load_sources()
    sources[name] = {
        "url": url,
        "priority": priority,
        "refresh_min": refresh_min,
    }
    save_sources(sources)
    return sources[name]


def remove_source(name):
    """remove a feed source."""
    sources = load_sources()
    if name in sources:
        del sources[name]
        save_sources(sources)
        return True
    return False


def set_priority(name, priority):
    """update source priority (1=highest, 5=lowest)."""
    sources = load_sources()
    if name in sources:
        sources[name]["priority"] = max(1, min(5, priority))
        save_sources(sources)
        return True
    return False


def sources_by_priority():
    """return sources sorted by priority (highest first)."""
    sources = load_sources()
    return sorted(
        sources.items(),
        key=lambda x: x[1].get("priority", 3)
    )


def due_for_refresh(name, last_refresh_time, current_time):
    """check if source is due for refresh."""
    sources = load_sources()
    source = sources.get(name)
    if not source:
        return False
    elapsed_min = (current_time - last_refresh_time) / 60
    return elapsed_min >= source.get("refresh_min", 60)


if __name__ == "__main__":
    sources = load_sources()
    print(f"configured sources: {len(sources)}")
    for name, config in sources_by_priority():
        print(f"  [{config['priority']}] {name}: {config['url'][:50]}")
