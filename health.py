#!/usr/bin/env python3
"""feed health monitoring - detect dead and stale feeds"""

import time
import urllib.request
import urllib.error
import json
from pathlib import Path

HEALTH_DIR = Path.home() / ".config" / "newk"
HEALTH_FILE = HEALTH_DIR / "feed_health.json"


def load_health_data():
    """load feed health data from disk"""
    if not HEALTH_FILE.exists():
        return {}
    try:
        with open(HEALTH_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_health_data(data):
    """save feed health data"""
    HEALTH_DIR.mkdir(parents=True, exist_ok=True)
    with open(HEALTH_FILE, "w") as f:
        json.dump(data, f, indent=2)


def check_feed(url, timeout=10):
    """check if a feed url is reachable and returns valid content"""
    result = {
        "url": url,
        "checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "unknown",
        "status_code": 0,
        "response_time": 0,
        "content_length": 0,
    }

    start = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "newk/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            result["status_code"] = resp.status
            result["content_length"] = len(data)
            result["response_time"] = round(time.time() - start, 2)

            if resp.status == 200 and len(data) > 100:
                result["status"] = "healthy"
            elif resp.status == 200:
                result["status"] = "empty"
            else:
                result["status"] = "error"

    except urllib.error.HTTPError as e:
        result["status_code"] = e.code
        result["status"] = "error"
        result["response_time"] = round(time.time() - start, 2)
    except (urllib.error.URLError, OSError):
        result["status"] = "unreachable"
        result["response_time"] = round(time.time() - start, 2)

    return result


def check_all_feeds(feed_urls, timeout=10):
    """check health of all feeds, returns list of results"""
    results = []
    for url in feed_urls:
        result = check_feed(url, timeout)
        results.append(result)
    return results


def update_health_history(results):
    """update persistent health tracking data"""
    history = load_health_data()

    for result in results:
        url = result["url"]
        if url not in history:
            history[url] = {"checks": [], "consecutive_failures": 0}

        entry = history[url]
        entry["checks"].append(result)
        entry["checks"] = entry["checks"][-30:]  # keep last 30 checks

        if result["status"] in ("error", "unreachable", "empty"):
            entry["consecutive_failures"] += 1
        else:
            entry["consecutive_failures"] = 0

        entry["last_checked"] = result["checked_at"]
        entry["last_status"] = result["status"]

    save_health_data(history)
    return history


def get_stale_feeds(max_failures=3):
    """get feeds that have failed consecutively"""
    history = load_health_data()
    stale = []
    for url, data in history.items():
        if data.get("consecutive_failures", 0) >= max_failures:
            stale.append({
                "url": url,
                "failures": data["consecutive_failures"],
                "last_status": data.get("last_status", "unknown"),
                "last_checked": data.get("last_checked", "never"),
            })
    return stale


def feed_health_summary(results):
    """generate summary of feed health check"""
    total = len(results)
    healthy = sum(1 for r in results if r["status"] == "healthy")
    errors = sum(1 for r in results if r["status"] == "error")
    unreachable = sum(1 for r in results if r["status"] == "unreachable")
    avg_time = sum(r["response_time"] for r in results) / max(total, 1)

    return {
        "total": total,
        "healthy": healthy,
        "errors": errors,
        "unreachable": unreachable,
        "avg_response_time": round(avg_time, 2),
    }
