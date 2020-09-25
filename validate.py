#!/usr/bin/env python3
"""validate feed urls and check for dead links"""

import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import URLError


FEEDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "feeds.txt")
RESEARCH_FEEDS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "research_feeds.txt"
)


def load_feeds(filename):
    """load feed urls from file"""
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        lines = f.read().strip().split("\n")
    return [l.strip() for l in lines if l.strip() and not l.startswith("#")]


def check_feed(url, timeout=10):
    """check if a feed url is reachable and returns valid content"""
    headers = {"User-Agent": "feed-validator/1.0"}
    req = Request(url, headers=headers)
    try:
        start = time.time()
        with urlopen(req, timeout=timeout) as resp:
            status = resp.getcode()
            content_type = resp.headers.get("Content-Type", "")
            size = len(resp.read(8192))
            elapsed = time.time() - start
            return {
                "url": url,
                "status": status,
                "content_type": content_type,
                "size": size,
                "time": round(elapsed, 2),
                "alive": True,
            }
    except (URLError, OSError) as e:
        return {
            "url": url,
            "error": str(e),
            "alive": False,
        }


def validate_all(verbose=True):
    """check all feeds and report dead links"""
    feeds = []
    for f in [FEEDS_FILE, RESEARCH_FEEDS_FILE]:
        feeds.extend(load_feeds(f))

    alive = []
    dead = []
    slow = []

    for i, url in enumerate(feeds):
        if verbose:
            print(f"  [{i + 1}/{len(feeds)}] {url[:70]}", end="", flush=True)

        result = check_feed(url)
        if result["alive"]:
            alive.append(result)
            if result["time"] > 5:
                slow.append(result)
            if verbose:
                print(f" ok ({result['time']}s)")
        else:
            dead.append(result)
            if verbose:
                print(f" DEAD ({result['error'][:50]})")

    return alive, dead, slow


def main():
    print("validating feeds...\n")
    alive, dead, slow = validate_all()

    print(f"\nalive: {len(alive)}  dead: {len(dead)}  slow: {len(slow)}")

    if dead:
        print("\ndead feeds:")
        for d in dead:
            print(f"  {d['url']}")
            print(f"    {d['error'][:80]}")

    if slow:
        print("\nslow feeds (>5s):")
        for s in slow:
            print(f"  {s['url']} ({s['time']}s)")


if __name__ == "__main__":
    main()
