#!/usr/bin/env python3
"""scrape: pull from all RSS/API sources, deduplicate, sort by recency"""

import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.request import urlopen, Request
from urllib.error import URLError


FEEDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "feeds.txt")
RESEARCH_FEEDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "research_feeds.txt")
CATEGORIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "categories.json")
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scrape_cache.json")


def load_feed_urls(filename):
    """load feed urls from a text file, one per line."""
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        lines = f.read().strip().split("\n")
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def load_categories():
    """load category definitions from categories.json."""
    if not os.path.exists(CATEGORIES_FILE):
        return {}
    with open(CATEGORIES_FILE, "r") as f:
        return json.load(f)


def url_to_category(url, categories):
    """look up which category a feed url belongs to."""
    for cat_name, cat_data in categories.items():
        for subcat_name, urls in cat_data.get("subcategories", {}).items():
            if url in urls:
                return cat_name, subcat_name
    return "uncategorized", "general"


def fetch_url(url, timeout=15):
    """fetch url content as bytes."""
    headers = {"User-Agent": "research-scraper/1.0"}
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (URLError, OSError) as e:
        print(f"  error: {url}: {e}", file=sys.stderr)
        return None


def parse_rss_date(date_str):
    """parse various date formats found in rss feeds.

    returns iso format string or empty string on failure.
    """
    if not date_str:
        return ""

    try:
        dt = parsedate_to_datetime(date_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        pass

    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    return date_str.strip()


def parse_feed(raw_bytes, source_url):
    """parse rss or atom feed xml into list of item dicts.

    handles both rss 2.0 and atom feed formats.
    """
    if raw_bytes is None:
        return []

    try:
        root = ET.fromstring(raw_bytes)
    except ET.ParseError:
        return []

    items = []
    for item in root.iter("item"):
        title_el = item.find("title")
        link_el = item.find("link")
        pub_el = item.find("pubDate")
        desc_el = item.find("description")

        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        link = link_el.text.strip() if link_el is not None and link_el.text else ""
        pub_date = pub_el.text.strip() if pub_el is not None and pub_el.text else ""
        description = desc_el.text.strip() if desc_el is not None and desc_el.text else ""

        if title:
            items.append({
                "title": title,
                "link": link,
                "date": parse_rss_date(pub_date),
                "description": description[:500] if description else "",
                "source": source_url,
            })

    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title_el = entry.find("{http://www.w3.org/2005/Atom}title")
        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
        updated_el = entry.find("{http://www.w3.org/2005/Atom}updated")
        published_el = entry.find("{http://www.w3.org/2005/Atom}published")
        summary_el = entry.find("{http://www.w3.org/2005/Atom}summary")

        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        link = link_el.get("href", "") if link_el is not None else ""
        date_str = ""
        if published_el is not None and published_el.text:
            date_str = published_el.text.strip()
        elif updated_el is not None and updated_el.text:
            date_str = updated_el.text.strip()
        description = summary_el.text.strip() if summary_el is not None and summary_el.text else ""

        if title:
            items.append({
                "title": title,
                "link": link,
                "date": parse_rss_date(date_str),
                "description": description[:500] if description else "",
                "source": source_url,
            })

    return items


def item_hash(item):
    """generate a deduplication hash for a feed item."""
    key = (item.get("title", "") + item.get("link", "")).lower().strip()
    return hashlib.md5(key.encode()).hexdigest()


def deduplicate(items):
    """remove duplicate items based on title+link hash."""
    seen = set()
    unique = []
    for item in items:
        h = item_hash(item)
        if h not in seen:
            seen.add(h)
            unique.append(item)
    return unique


def sort_by_recency(items):
    """sort items by date, most recent first.

    items without dates go to the end.
    """
    def sort_key(item):
        d = item.get("date", "")
        if d:
            return d
        return "0000-00-00"

    items.sort(key=sort_key, reverse=True)
    return items


def load_cache():
    """load previously scraped items from cache file."""
    if not os.path.exists(CACHE_FILE):
        return []
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def save_cache(items, max_items=5000):
    """save scraped items to cache file, keeping most recent."""
    items = items[:max_items]
    with open(CACHE_FILE, "w") as f:
        json.dump(items, f, indent=2)


def scrape_all(feed_files=None, max_per_feed=20, verbose=True):
    """scrape all feeds and return deduplicated, sorted items.

    reads feed urls from feeds.txt and research_feeds.txt.
    fetches each feed, parses items, deduplicates, and sorts.
    """
    if feed_files is None:
        feed_files = [FEEDS_FILE, RESEARCH_FEEDS_FILE]

    all_urls = []
    for ff in feed_files:
        all_urls.extend(load_feed_urls(ff))

    categories = load_categories()
    all_items = []
    errors = 0

    for i, url in enumerate(all_urls):
        if verbose:
            print(f"  [{i + 1}/{len(all_urls)}] {url[:80]}", file=sys.stderr)

        raw = fetch_url(url)
        if raw is None:
            errors += 1
            continue

        items = parse_feed(raw, url)
        cat, subcat = url_to_category(url, categories)
        for item in items[:max_per_feed]:
            item["category"] = cat
            item["subcategory"] = subcat
        all_items.extend(items[:max_per_feed])

    all_items = deduplicate(all_items)
    all_items = sort_by_recency(all_items)

    if verbose:
        print(f"\n  feeds: {len(all_urls)}  items: {len(all_items)}"
              f"  errors: {errors}", file=sys.stderr)

    return all_items


def print_items(items, limit=50, show_category=False):
    """print items to stdout in a readable format."""
    for item in items[:limit]:
        date = item.get("date", "")[:10]
        title = item.get("title", "")[:100]
        cat = f" [{item.get('category', '')}]" if show_category else ""
        print(f"  {date}  {title}{cat}")


def main():
    if "--help" in sys.argv:
        print("usage: python scrape.py [options]")
        print("  --json          output as json")
        print("  --limit N       max items to show (default 50)")
        print("  --category C    filter by category")
        print("  --categories    show category summary")
        print("  --cache         use cached data if available")
        print("  --save          save results to cache")
        sys.exit(0)

    as_json = "--json" in sys.argv
    show_categories = "--categories" in sys.argv
    use_cache = "--cache" in sys.argv
    save = "--save" in sys.argv
    limit = 50
    category_filter = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--limit":
            limit = int(args[i + 1])
            i += 2
        elif args[i] == "--category":
            category_filter = args[i + 1].lower()
            i += 2
        else:
            i += 1

    if use_cache:
        items = load_cache()
        if items:
            print(f"loaded {len(items)} cached items", file=sys.stderr)
        else:
            print("no cache found, scraping fresh", file=sys.stderr)
            items = scrape_all()
    else:
        print("scraping feeds...", file=sys.stderr)
        items = scrape_all()

    if save:
        save_cache(items)
        print(f"saved {len(items)} items to cache", file=sys.stderr)

    if category_filter:
        items = [it for it in items if it.get("category", "") == category_filter]

    if show_categories:
        cat_counts = {}
        for it in items:
            cat = it.get("category", "uncategorized")
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        print(f"\ncategory summary ({len(items)} items):")
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {count}")
        return

    if as_json:
        print(json.dumps(items[:limit], indent=2))
    else:
        print(f"\nlatest items ({min(limit, len(items))} of {len(items)}):")
        print_items(items, limit, show_category=True)


if __name__ == "__main__":
    main()
