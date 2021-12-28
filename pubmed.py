#!/usr/bin/env python3
"""pubmed feed parser for health research tracking"""

import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request


PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def search_pubmed(query, max_results=20):
    """search pubmed for articles matching query.

    returns list of pubmed ids.
    """
    url = (f"{PUBMED_BASE}/esearch.fcgi?db=pubmed"
           f"&term={query}&retmax={max_results}&retmode=xml")
    try:
        req = Request(url, headers={"User-Agent": "research-feed/1.0"})
        resp = urlopen(req, timeout=10)
        root = ET.fromstring(resp.read())
        return [id_elem.text for id_elem in root.findall(".//Id")]
    except (OSError, ET.ParseError):
        return []


def fetch_abstracts(pmids):
    """fetch article details for a list of pubmed ids."""
    if not pmids:
        return []
    ids = ",".join(pmids)
    url = (f"{PUBMED_BASE}/efetch.fcgi?db=pubmed"
           f"&id={ids}&retmode=xml")
    try:
        req = Request(url, headers={"User-Agent": "research-feed/1.0"})
        resp = urlopen(req, timeout=15)
        return parse_articles(resp.read())
    except (OSError, ET.ParseError):
        return []


def parse_articles(xml_data):
    """parse pubmed xml response into article dicts."""
    articles = []
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        return []
    for article in root.findall(".//PubmedArticle"):
        title_elem = article.find(".//ArticleTitle")
        abstract_elem = article.find(".//AbstractText")
        pmid_elem = article.find(".//PMID")
        journal_elem = article.find(".//Journal/Title")
        year_elem = article.find(".//PubDate/Year")
        mesh_terms = [
            m.text for m in article.findall(".//MeshHeading/DescriptorName")
            if m.text
        ]
        articles.append({
            "pmid": pmid_elem.text if pmid_elem is not None else "",
            "title": title_elem.text if title_elem is not None else "",
            "abstract": abstract_elem.text if abstract_elem is not None else "",
            "journal": journal_elem.text if journal_elem is not None else "",
            "year": year_elem.text if year_elem is not None else "",
            "mesh_terms": mesh_terms,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid_elem.text}/"
            if pmid_elem is not None else "",
        })
    return articles


def filter_by_mesh(articles, terms):
    """filter articles by mesh term keywords."""
    terms_lower = [t.lower() for t in terms]
    return [
        a for a in articles
        if any(t.lower() in m.lower() for t in terms_lower for m in a.get("mesh_terms", []))
    ]


if __name__ == "__main__":
    print("pubmed feed parser")
    print("usage: search_pubmed('covid vaccine', max_results=5)")
