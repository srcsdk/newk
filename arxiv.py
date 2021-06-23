#!/usr/bin/env python3
"""arxiv feed parser for academic paper tracking"""

import xml.etree.ElementTree as ET
import re
import urllib.request
import urllib.error

ARXIV_BASE = "http://export.arxiv.org/api/query"
ARXIV_RSS = "http://export.arxiv.org/rss"

CATEGORIES = {
    "cs.AI": "artificial intelligence",
    "cs.LG": "machine learning",
    "cs.CR": "cryptography and security",
    "cs.CL": "computation and language",
    "cs.CV": "computer vision",
    "cs.NE": "neural and evolutionary computing",
    "cs.SE": "software engineering",
    "stat.ML": "machine learning (statistics)",
    "q-fin.ST": "statistical finance",
    "q-fin.PM": "portfolio management",
    "q-fin.RM": "risk management",
}


def fetch_arxiv_rss(category):
    """fetch latest papers from an arxiv category rss feed"""
    url = f"{ARXIV_RSS}/{category}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "newk/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        return parse_arxiv_rss(data, category)
    except (urllib.error.URLError, OSError):
        return []


def parse_arxiv_rss(data, category):
    """parse arxiv rss xml into article dicts"""
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return []

    ns = {"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
          "rss": "http://purl.org/rss/1.0/",
          "dc": "http://purl.org/dc/elements/1.1/"}

    articles = []
    for item in root.findall(".//item"):
        if item is None:
            continue
        title_el = item.find("title")
        link_el = item.find("link")
        desc_el = item.find("description")

        if title_el is None:
            continue

        title = title_el.text or ""
        # clean arxiv title format
        title = re.sub(r"\s*\(arXiv:[\d.]+v\d+.*?\)", "", title).strip()

        link = link_el.text.strip() if link_el is not None and link_el.text else ""
        desc = desc_el.text.strip() if desc_el is not None and desc_el.text else ""

        # extract arxiv id from link
        arxiv_id = ""
        id_match = re.search(r"(\d{4}\.\d{4,5})", link)
        if id_match:
            arxiv_id = id_match.group(1)

        # extract authors from description
        authors = []
        author_match = re.search(r"<dc:creator[^>]*>(.*?)</dc:creator>", desc)
        if author_match:
            authors = [a.strip() for a in author_match.group(1).split(",")]

        # clean html from description
        clean_desc = re.sub(r"<[^>]+>", "", desc).strip()

        articles.append({
            "title": title,
            "link": link,
            "arxiv_id": arxiv_id,
            "authors": authors,
            "abstract": clean_desc[:500],
            "category": category,
            "category_name": CATEGORIES.get(category, category),
            "source": f"arxiv:{category}",
        })

    return articles


def search_arxiv(query, max_results=20):
    """search arxiv api for papers matching a query"""
    params = urllib.parse.urlencode({
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    url = f"{ARXIV_BASE}?{params}"

    try:
        import urllib.parse
        req = urllib.request.Request(url, headers={"User-Agent": "newk/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        return parse_arxiv_api(data)
    except (urllib.error.URLError, OSError):
        return []


def parse_arxiv_api(data):
    """parse arxiv api atom response"""
    ns = {"atom": "http://www.w3.org/2005/Atom",
          "arxiv": "http://arxiv.org/schemas/atom"}

    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return []

    articles = []
    for entry in root.findall("atom:entry", ns):
        title_el = entry.find("atom:title", ns)
        summary_el = entry.find("atom:summary", ns)
        id_el = entry.find("atom:id", ns)

        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        title = re.sub(r"\s+", " ", title)

        summary = summary_el.text.strip() if summary_el is not None and summary_el.text else ""
        summary = re.sub(r"\s+", " ", summary)

        link = id_el.text.strip() if id_el is not None and id_el.text else ""

        authors = []
        for author in entry.findall("atom:author", ns):
            name_el = author.find("atom:name", ns)
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())

        cats = []
        for cat in entry.findall("atom:category", ns):
            term = cat.get("term", "")
            if term:
                cats.append(term)

        articles.append({
            "title": title,
            "link": link,
            "authors": authors,
            "abstract": summary[:500],
            "categories": cats,
            "source": "arxiv",
        })

    return articles


def get_available_categories():
    """return dict of available arxiv categories"""
    return CATEGORIES.copy()
