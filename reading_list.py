#!/usr/bin/env python3
"""reading list management for saved articles"""

import json
import os
import time


class ReadingList:
    """manage saved articles for later reading."""

    def __init__(self, filepath="reading_list.json"):
        self.filepath = filepath
        self.items = self._load()

    def save_article(self, article, tags=None):
        """save an article to the reading list."""
        item = {
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "source": article.get("source", ""),
            "tags": tags or [],
            "saved_at": time.time(),
            "read": False,
            "notes": "",
        }
        self.items.append(item)
        self._save()
        return item

    def mark_read(self, index):
        """mark an article as read."""
        if 0 <= index < len(self.items):
            self.items[index]["read"] = True
            self.items[index]["read_at"] = time.time()
            self._save()
            return True
        return False

    def add_note(self, index, note):
        """add a note to a saved article."""
        if 0 <= index < len(self.items):
            self.items[index]["notes"] = note
            self._save()
            return True
        return False

    def unread(self):
        """get unread articles."""
        return [i for i in self.items if not i.get("read")]

    def by_tag(self, tag):
        """filter articles by tag."""
        return [i for i in self.items if tag in i.get("tags", [])]

    def search(self, query):
        """search reading list by title."""
        query_lower = query.lower()
        return [
            i for i in self.items
            if query_lower in i.get("title", "").lower()
        ]

    def remove(self, index):
        """remove an article from the list."""
        if 0 <= index < len(self.items):
            removed = self.items.pop(index)
            self._save()
            return removed
        return None

    def stats(self):
        """reading list statistics."""
        total = len(self.items)
        read = sum(1 for i in self.items if i.get("read"))
        return {
            "total": total,
            "read": read,
            "unread": total - read,
        }

    def _load(self):
        if os.path.isfile(self.filepath):
            with open(self.filepath) as f:
                return json.load(f)
        return []

    def _save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.items, f, indent=2)


if __name__ == "__main__":
    rl = ReadingList("/tmp/test_reading.json")
    rl.save_article(
        {"title": "python 3.11 features", "url": "example.com/py311"},
        tags=["python"],
    )
    rl.save_article(
        {"title": "linux kernel internals", "url": "example.com/kernel"},
        tags=["linux"],
    )
    stats = rl.stats()
    print(f"reading list: {stats}")
    unread = rl.unread()
    for item in unread:
        print(f"  {item['title']}")
