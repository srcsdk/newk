#!/usr/bin/env python3
"""finance category with market data and economic feeds"""

FINANCE_FEEDS = [
    # economic data releases
    {"url": "https://www.bls.gov/feed/bls_latest.rss",
     "title": "bureau of labor statistics",
     "category": "economics"},
    {"url": "https://www.census.gov/economic-indicators/indicator.xml",
     "title": "us census economic indicators",
     "category": "economics"},
    {"url": "https://www.federalreserve.gov/feeds/press_all.xml",
     "title": "federal reserve press releases",
     "category": "monetary_policy"},

    # market research
    {"url": "https://www.nber.org/rss/new.xml",
     "title": "nber working papers",
     "category": "research"},
    {"url": "https://papers.ssrn.com/sol3/Jeljour_results.cfm?"
     "form_name=journalBrowse&journal_id=556&Network=no&"
     "lim=false&npage=1&SortOrder=ab_approval_date&stype=desc&output=rss",
     "title": "ssrn finance",
     "category": "research"},

    # sec filings
    {"url": "https://www.sec.gov/cgi-bin/browse-edgar?"
     "action=getcurrent&type=10-K&dateb=&owner=include&count=20&"
     "search_text=&action=getcurrent&output=atom",
     "title": "sec 10-k filings",
     "category": "filings"},

    # financial news
    {"url": "https://feeds.finance.yahoo.com/rss/2.0/"
     "headline?s=^GSPC&region=US&lang=en-US",
     "title": "yahoo finance sp500",
     "category": "markets"},
]

FINANCE_SUBCATEGORIES = {
    "economics": "economic data and indicators",
    "monetary_policy": "central bank decisions and policy",
    "research": "academic finance research",
    "filings": "regulatory filings and disclosures",
    "markets": "market news and analysis",
}


def get_finance_feeds():
    """return list of finance feed configs"""
    return FINANCE_FEEDS.copy()


def get_finance_subcategories():
    """return finance subcategory descriptions"""
    return FINANCE_SUBCATEGORIES.copy()


def filter_by_subcategory(feeds, subcategory):
    """filter finance feeds by subcategory"""
    return [f for f in feeds if f.get("category") == subcategory]


def get_feed_urls():
    """return just the urls for all finance feeds"""
    return [f["url"] for f in FINANCE_FEEDS]


def format_finance_feed_list():
    """format finance feeds for display"""
    lines = []
    for subcat, desc in FINANCE_SUBCATEGORIES.items():
        lines.append(f"\n{subcat}: {desc}")
        for feed in filter_by_subcategory(FINANCE_FEEDS, subcat):
            lines.append(f"  {feed['title']}")
            lines.append(f"    {feed['url'][:80]}")
    return "\n".join(lines)
