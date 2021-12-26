#!/usr/bin/env python3
"""keyword alerts for new articles matching user-defined terms"""

import json
import time
from pathlib import Path

ALERTS_DIR = Path.home() / ".config" / "newk"
ALERTS_FILE = ALERTS_DIR / "alerts.json"
ALERT_LOG_FILE = ALERTS_DIR / "alert_log.json"


def load_alerts():
    """load alert configurations"""
    if not ALERTS_FILE.exists():
        return []
    try:
        with open(ALERTS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_alerts(alerts):
    """save alert configurations"""
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)


def create_alert(name, keywords, categories=None, match_mode="any"):
    """create a new keyword alert.

    match_mode: 'any' matches if any keyword found, 'all' requires all
    """
    alerts = load_alerts()
    alert = {
        "name": name,
        "keywords": keywords if isinstance(keywords, list) else [keywords],
        "categories": categories or [],
        "match_mode": match_mode,
        "enabled": True,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    alerts.append(alert)
    save_alerts(alerts)
    return alert


def remove_alert(name):
    """remove an alert by name"""
    alerts = load_alerts()
    alerts = [a for a in alerts if a["name"] != name]
    save_alerts(alerts)


def check_article(article, alerts=None):
    """check if an article matches any active alerts.

    returns list of matching alert names
    """
    if alerts is None:
        alerts = load_alerts()

    title = article.get("title", "").lower()
    desc = article.get("description", article.get("abstract", "")).lower()
    source = article.get("source", "").lower()
    content = f"{title} {desc} {source}"

    matches = []
    for alert in alerts:
        if not alert.get("enabled", True):
            continue

        # category filter
        if alert.get("categories"):
            article_cat = article.get("category", "")
            if article_cat and article_cat not in alert["categories"]:
                continue

        keywords = alert["keywords"]
        mode = alert.get("match_mode", "any")

        if mode == "all":
            if all(kw.lower() in content for kw in keywords):
                matches.append(alert["name"])
        else:
            if any(kw.lower() in content for kw in keywords):
                matches.append(alert["name"])

    return matches


def check_articles(articles, alerts=None):
    """check multiple articles against alerts.

    returns list of (article, matching_alerts) tuples for matches
    """
    if alerts is None:
        alerts = load_alerts()

    results = []
    for article in articles:
        matching = check_article(article, alerts)
        if matching:
            results.append((article, matching))

    return results


def log_alert_match(article, alert_names):
    """log an alert match for history"""
    log = []
    if ALERT_LOG_FILE.exists():
        try:
            with open(ALERT_LOG_FILE) as f:
                log = json.load(f)
        except (json.JSONDecodeError, OSError):
            log = []

    log.append({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "title": article.get("title", ""),
        "link": article.get("link", ""),
        "alerts": alert_names,
    })

    # keep last 500 entries
    log = log[-500:]
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ALERT_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)
