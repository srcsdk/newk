#!/usr/bin/env python3
"""tag feeds and items with interest keywords for personalized filtering"""

import json
import os

TAGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tags.json")


def load_tags():
    """load user-defined interest tags"""
    if not os.path.exists(TAGS_FILE):
        return {"feed_tags": {}, "keyword_tags": {}}
    try:
        with open(TAGS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {"feed_tags": {}, "keyword_tags": {}}


def save_tags(tags):
    """save tags to file"""
    with open(TAGS_FILE, "w") as f:
        json.dump(tags, f, indent=2)


def tag_feed(url, tag_name):
    """add a tag to a feed url"""
    tags = load_tags()
    if url not in tags["feed_tags"]:
        tags["feed_tags"][url] = []
    if tag_name not in tags["feed_tags"][url]:
        tags["feed_tags"][url].append(tag_name)
    save_tags(tags)


def add_keyword_tag(keyword, tag_name):
    """auto-tag items containing a keyword"""
    tags = load_tags()
    if tag_name not in tags["keyword_tags"]:
        tags["keyword_tags"][tag_name] = []
    if keyword not in tags["keyword_tags"][tag_name]:
        tags["keyword_tags"][tag_name].append(keyword)
    save_tags(tags)


def tag_item(item, tags=None):
    """apply tags to an item based on feed url and keyword matches"""
    if tags is None:
        tags = load_tags()

    item_tags = set()

    # check feed-level tags
    source = item.get("source", "")
    if source in tags.get("feed_tags", {}):
        item_tags.update(tags["feed_tags"][source])

    # check keyword tags
    title = item.get("title", "").lower()
    desc = item.get("description", "").lower()
    text = title + " " + desc

    for tag_name, keywords in tags.get("keyword_tags", {}).items():
        for kw in keywords:
            if kw.lower() in text:
                item_tags.add(tag_name)
                break

    return list(item_tags)


def filter_by_tag(items, tag_name, tags=None):
    """filter items to only those matching a specific tag"""
    if tags is None:
        tags = load_tags()

    result = []
    for item in items:
        item_tags = tag_item(item, tags)
        if tag_name in item_tags:
            result.append(item)
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: python tags.py <command>")
        print("  list           show all tags")
        print("  add-kw <kw> <tag>  add keyword tag")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "list":
        tags = load_tags()
        print("keyword tags:")
        for tag, keywords in tags.get("keyword_tags", {}).items():
            print(f"  {tag}: {', '.join(keywords)}")
        print(f"\nfeed tags: {len(tags.get('feed_tags', {}))}")
    elif cmd == "add-kw" and len(sys.argv) >= 4:
        add_keyword_tag(sys.argv[2], sys.argv[3])
        print(f"added keyword '{sys.argv[2]}' to tag '{sys.argv[3]}'")
