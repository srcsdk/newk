#!/usr/bin/env python3
"""feed source health check with uptime tracking"""

import json
import os
import time
from urllib.request import urlopen, Request


HEALTH_FILE = os.path.join(os.path.dirname(__file__), "feed_health.json")


def load_health():
    """load health tracking data."""
    if os.path.exists(HEALTH_FILE):
        with open(HEALTH_FILE, "r") as f:
            return json.load(f)
    return {}


def save_health(data):
    """save health data."""
    with open(HEALTH_FILE, "w") as f:
        json.dump(data, f, indent=2)


def check_feed(url, timeout=10):
    """check if a feed url is reachable."""
    start = time.time()
    try:
        req = Request(url, headers={"User-Agent": "feed-health/1.0"})
        resp = urlopen(req, timeout=timeout)
        elapsed = time.time() - start
        return {
            "status": "up",
            "response_time": round(elapsed, 3),
            "status_code": resp.getcode(),
            "timestamp": time.time(),
        }
    except OSError:
        return {
            "status": "down",
            "response_time": time.time() - start,
            "timestamp": time.time(),
        }


def update_health(url, check_result):
    """update health tracking for a feed url."""
    data = load_health()
    if url not in data:
        data[url] = {"checks": 0, "up": 0, "down": 0, "history": []}
    data[url]["checks"] += 1
    data[url][check_result["status"]] += 1
    data[url]["history"].append(check_result)
    data[url]["history"] = data[url]["history"][-100:]
    data[url]["uptime_pct"] = round(
        data[url]["up"] / data[url]["checks"] * 100, 1
    )
    save_health(data)
    return data[url]


def feed_report(data=None):
    """generate health report for all tracked feeds."""
    if data is None:
        data = load_health()
    report = []
    for url, info in data.items():
        avg_time = 0
        times = [h["response_time"] for h in info.get("history", [])
                 if h.get("status") == "up"]
        if times:
            avg_time = round(sum(times) / len(times), 3)
        report.append({
            "url": url,
            "uptime": info.get("uptime_pct", 0),
            "avg_response": avg_time,
            "total_checks": info.get("checks", 0),
        })
    return sorted(report, key=lambda r: r["uptime"])


if __name__ == "__main__":
    report = feed_report()
    print(f"tracking {len(report)} feeds")
    for r in report:
        print(f"  {r['uptime']}% up  {r['avg_response']}s  {r['url']}")
