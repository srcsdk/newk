#!/usr/bin/env python3
"""read-later queue for saving articles"""

import json
import os
import time
import hashlib


class ReadLaterQueue:
    """manage a queue of articles to read later."""

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.newk")
        self.data_dir = data_dir
        self.queue_file = os.path.join(data_dir, "read_later.json")
        os.makedirs(data_dir, exist_ok=True)
        self.items = self._load()

    def _load(self):
        if os.path.isfile(self.queue_file):
            with open(self.queue_file) as f:
                return json.load(f)
        return []

    def _save(self):
        with open(self.queue_file, "w") as f:
            json.dump(self.items, f, indent=2)

    def add(self, url, title="", tags=None):
        """add article to read-later queue."""
        item_id = hashlib.md5(url.encode()).hexdigest()[:10]
        for item in self.items:
            if item["url"] == url:
                return item
        item = {
            "id": item_id,
            "url": url,
            "title": title,
            "tags": tags or [],
            "added": time.strftime("%Y-%m-%d %H:%M"),
            "read": False,
        }
        self.items.append(item)
        self._save()
        return item

    def mark_read(self, item_id):
        """mark an item as read."""
        for item in self.items:
            if item["id"] == item_id:
                item["read"] = True
                item["read_at"] = time.strftime("%Y-%m-%d %H:%M")
                self._save()
                return True
        return False

    def unread(self):
        """get unread items."""
        return [i for i in self.items if not i.get("read")]

    def by_tag(self, tag):
        """filter items by tag."""
        return [i for i in self.items if tag in i.get("tags", [])]

    def remove(self, item_id):
        """remove item from queue."""
        self.items = [i for i in self.items if i["id"] != item_id]
        self._save()

    def stats(self):
        """queue statistics."""
        total = len(self.items)
        read = sum(1 for i in self.items if i.get("read"))
        return {"total": total, "read": read, "unread": total - read}


if __name__ == "__main__":
    q = ReadLaterQueue("/tmp/newk_test")
    q.add("https://example.com/article1", "test article", ["tech"])
    q.add("https://example.com/article2", "another article", ["science"])
    print(f"queue: {q.stats()}")
    print(f"unread: {len(q.unread())}")
