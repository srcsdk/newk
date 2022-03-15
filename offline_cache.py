#!/usr/bin/env python3
"""offline content caching for articles"""

import os
import json
import hashlib
import time
from urllib.request import urlopen, Request
from urllib.error import URLError


class OfflineCache:
    """cache article content for offline reading."""

    def __init__(self, cache_dir=None):
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.newk/cache")
        self.cache_dir = cache_dir
        self.index_file = os.path.join(cache_dir, "index.json")
        os.makedirs(cache_dir, exist_ok=True)
        self.index = self._load_index()

    def _load_index(self):
        if os.path.isfile(self.index_file):
            with open(self.index_file) as f:
                return json.load(f)
        return {}

    def _save_index(self):
        with open(self.index_file, "w") as f:
            json.dump(self.index, f, indent=2)

    def cache_url(self, url):
        """download and cache a url."""
        key = hashlib.md5(url.encode()).hexdigest()
        try:
            req = Request(url, headers={"User-Agent": "newk/1.0"})
            resp = urlopen(req, timeout=15)
            content = resp.read()
        except (URLError, OSError):
            return None
        cache_path = os.path.join(self.cache_dir, f"{key}.html")
        with open(cache_path, "wb") as f:
            f.write(content)
        self.index[key] = {
            "url": url,
            "cached_at": time.strftime("%Y-%m-%d %H:%M"),
            "size": len(content),
            "path": cache_path,
        }
        self._save_index()
        return cache_path

    def get_cached(self, url):
        """retrieve cached content for a url."""
        key = hashlib.md5(url.encode()).hexdigest()
        entry = self.index.get(key)
        if not entry:
            return None
        path = entry.get("path", "")
        if os.path.isfile(path):
            with open(path, "rb") as f:
                return f.read()
        return None

    def is_cached(self, url):
        """check if url is cached."""
        key = hashlib.md5(url.encode()).hexdigest()
        return key in self.index

    def cache_size(self):
        """total size of cache in bytes."""
        return sum(e.get("size", 0) for e in self.index.values())

    def clear_old(self, max_age_days=30):
        """remove cache entries older than max_age_days."""
        cutoff = time.time() - (max_age_days * 86400)
        to_remove = []
        for key, entry in self.index.items():
            path = entry.get("path", "")
            if os.path.isfile(path):
                if os.path.getmtime(path) < cutoff:
                    os.remove(path)
                    to_remove.append(key)
        for key in to_remove:
            del self.index[key]
        self._save_index()
        return len(to_remove)

    def clear_all(self):
        """clear entire cache."""
        for entry in self.index.values():
            path = entry.get("path", "")
            if os.path.isfile(path):
                os.remove(path)
        self.index.clear()
        self._save_index()


if __name__ == "__main__":
    cache = OfflineCache("/tmp/newk_cache")
    print(f"cache entries: {len(cache.index)}")
    print(f"cache size: {cache.cache_size()} bytes")
