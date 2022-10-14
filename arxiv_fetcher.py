#!/usr/bin/env python3
"""fetch and parse research papers from arxiv"""

import xml.etree.ElementTree as ET
import re


class ArxivFetcher:
    """fetch research papers from arxiv api."""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self):
        self.cache = {}
        self.categories = {
            "cs.AI": "artificial intelligence",
            "cs.CR": "cryptography and security",
            "cs.LG": "machine learning",
            "cs.SE": "software engineering",
            "cs.DS": "data structures and algorithms",
            "cs.DC": "distributed computing",
            "cs.NI": "networking",
            "stat.ML": "statistical ml",
            "q-fin.ST": "quantitative finance",
        }

    def build_query(self, search_term=None, category=None,
                    max_results=20, start=0):
        """build arxiv api query url."""
        params = []
        query_parts = []
        if search_term:
            query_parts.append(f"all:{search_term}")
        if category:
            query_parts.append(f"cat:{category}")
        if query_parts:
            params.append(f"search_query={'+AND+'.join(query_parts)}")
        params.append(f"start={start}")
        params.append(f"max_results={max_results}")
        params.append("sortBy=submittedDate")
        params.append("sortOrder=descending")
        return f"{self.BASE_URL}?{'&'.join(params)}"

    def parse_response(self, xml_text):
        """parse arxiv api xml response."""
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return []
        entries = root.findall("atom:entry", ns)
        papers = []
        for entry in entries:
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            published = entry.find("atom:published", ns)
            authors = entry.findall("atom:author/atom:name", ns)
            links = entry.findall("atom:link", ns)
            pdf_url = ""
            for link in links:
                if link.get("title") == "pdf":
                    pdf_url = link.get("href", "")
            categories = entry.findall(
                "{http://arxiv.org/schemas/atom}primary_category"
            )
            cat = categories[0].get("term", "") if categories else ""
            paper = {
                "title": self._clean_text(title.text if title is not None else ""),
                "summary": self._clean_text(
                    summary.text if summary is not None else ""
                ),
                "published": published.text if published is not None else "",
                "authors": [a.text for a in authors],
                "pdf_url": pdf_url,
                "category": cat,
            }
            papers.append(paper)
        return papers

    def _clean_text(self, text):
        """clean whitespace from text."""
        return re.sub(r'\s+', ' ', text).strip()

    def list_categories(self):
        """list available arxiv categories."""
        return dict(self.categories)

    def format_paper(self, paper):
        """format paper for display."""
        authors = ", ".join(paper["authors"][:3])
        if len(paper["authors"]) > 3:
            authors += f" (+{len(paper['authors']) - 3})"
        return {
            "title": paper["title"],
            "authors": authors,
            "date": paper["published"][:10],
            "category": paper["category"],
            "summary": paper["summary"][:300],
        }


if __name__ == "__main__":
    fetcher = ArxivFetcher()
    url = fetcher.build_query(search_term="transformer", category="cs.AI")
    print(f"query url: {url}")
    cats = fetcher.list_categories()
    for cat, desc in cats.items():
        print(f"  {cat}: {desc}")
