#!/usr/bin/env python3
"""api_feeds: fetch data from FRED and SEC EDGAR APIs, output JSON"""

import json
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError


FRED_SERIES = {
    "DGS10": "10-year treasury yield",
    "DGS2": "2-year treasury yield",
    "FEDFUNDS": "federal funds rate",
    "UNRATE": "unemployment rate",
    "CPIAUCSL": "consumer price index",
    "GDP": "gross domestic product",
    "T10Y2Y": "10y-2y treasury spread",
    "VIXCLS": "vix close",
}

EDGAR_SEARCH_URL = (
    "https://efts.sec.gov/LATEST/search-index"
    "?q=&forms={form_type}&dateRange=custom"
    "&startdt={start}&enddt={end}"
)

EDGAR_FILINGS_URL = (
    "https://data.sec.gov/submissions/CIK{cik}.json"
)


def fetch_url(url, timeout=15):
    """fetch url and return parsed content."""
    headers = {"User-Agent": "research-bot/1.0 (academic use)"}
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (URLError, OSError) as e:
        print(f"fetch error {url}: {e}", file=sys.stderr)
        return None


def fetch_json(url, timeout=15):
    """fetch url and parse as json."""
    raw = fetch_url(url, timeout)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None


def fetch_fred_series(series_id, limit=10):
    """fetch recent observations from FRED for a given series.

    uses the public FRED observations endpoint (no API key needed for
    basic access via the html/json endpoint).
    returns list of date/value pairs.
    """
    url = (
        f"https://fred.stlouisfed.org/graph/fredgraph.csv"
        f"?id={series_id}&cosd=2024-01-01"
    )
    raw = fetch_url(url)
    if raw is None:
        return None

    lines = raw.decode("utf-8", errors="replace").strip().split("\n")
    if len(lines) < 2:
        return None

    results = []
    for line in lines[1:]:
        parts = line.strip().split(",")
        if len(parts) >= 2:
            date_str = parts[0]
            value_str = parts[1]
            if value_str == ".":
                continue
            try:
                value = float(value_str)
                results.append({"date": date_str, "value": value})
            except ValueError:
                continue

    if limit and len(results) > limit:
        results = results[-limit:]
    return results


def fetch_fred_all(limit=5):
    """fetch all configured FRED series and return combined dict."""
    output = {}
    for series_id, description in FRED_SERIES.items():
        data = fetch_fred_series(series_id, limit=limit)
        output[series_id] = {
            "description": description,
            "observations": data if data else [],
        }
    return output


def fetch_edgar_recent(form_type="8-K", count=10):
    """fetch recent SEC EDGAR filings by form type.

    uses the full-text search endpoint for recent filings.
    returns list of filing metadata.
    """
    url = (
        f"https://efts.sec.gov/LATEST/search-index"
        f"?q=&forms={form_type}&dateRange=custom"
        f"&startdt=2025-01-01&enddt=2026-12-31"
    )
    data = fetch_json(url)
    if not data:
        return []

    hits = data.get("hits", {}).get("hits", [])
    results = []
    for hit in hits[:count]:
        source = hit.get("_source", {})
        results.append({
            "company": source.get("display_names", [""])[0] if source.get("display_names") else "",
            "form_type": source.get("form_type", ""),
            "filed": source.get("file_date", ""),
            "description": source.get("display_description", ""),
        })

    return results


def fetch_edgar_company(cik, count=5):
    """fetch recent filings for a specific company by CIK number.

    pads CIK to 10 digits and queries the submissions endpoint.
    """
    cik_padded = str(cik).zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    data = fetch_json(url)
    if not data:
        return None

    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    descriptions = recent.get("primaryDocDescription", [])

    results = []
    for i in range(min(count, len(forms))):
        results.append({
            "form": forms[i] if i < len(forms) else "",
            "date": dates[i] if i < len(dates) else "",
            "description": descriptions[i] if i < len(descriptions) else "",
        })

    return {
        "name": data.get("name", ""),
        "cik": cik,
        "filings": results,
    }


def main():
    if len(sys.argv) < 2:
        print("usage: python api_feeds.py <command> [options]")
        print("  fred                fetch all FRED series")
        print("  fred <series_id>    fetch specific FRED series")
        print("  edgar               fetch recent 8-K filings")
        print("  edgar <form_type>   fetch specific form type")
        print("  company <cik>       fetch company filings by CIK")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "fred":
        if len(sys.argv) > 2:
            series_id = sys.argv[2].upper()
            data = fetch_fred_series(series_id, limit=20)
            output = {series_id: {
                "description": FRED_SERIES.get(series_id, series_id),
                "observations": data if data else [],
            }}
        else:
            output = fetch_fred_all()
        print(json.dumps(output, indent=2))

    elif command == "edgar":
        form_type = sys.argv[2] if len(sys.argv) > 2 else "8-K"
        filings = fetch_edgar_recent(form_type=form_type)
        print(json.dumps(filings, indent=2))

    elif command == "company":
        if len(sys.argv) < 3:
            print("usage: python api_feeds.py company <cik>", file=sys.stderr)
            sys.exit(1)
        cik = sys.argv[2]
        data = fetch_edgar_company(cik)
        print(json.dumps(data, indent=2))

    else:
        print(f"unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
