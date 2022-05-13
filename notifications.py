#!/usr/bin/env python3
"""notification system for breaking news and trending topics"""

import json
import os


class NotificationManager:
    """manage user notifications for feed events."""

    def __init__(self, config_path="notifications.json"):
        self.config_path = config_path
        self.rules = self._load_rules()
        self.pending = []
        self.history = []

    def add_rule(self, name, keywords=None, sources=None,
                 priority="normal"):
        """add a notification rule."""
        rule = {
            "name": name,
            "keywords": keywords or [],
            "sources": sources or [],
            "priority": priority,
            "active": True,
        }
        self.rules.append(rule)
        self._save_rules()
        return rule

    def check_article(self, article):
        """check if article triggers any notification rules."""
        notifications = []
        title = article.get("title", "").lower()
        source = article.get("source", "").lower()
        text = article.get("text", "").lower()
        for rule in self.rules:
            if not rule.get("active"):
                continue
            triggered = False
            for keyword in rule.get("keywords", []):
                if keyword.lower() in title or keyword.lower() in text:
                    triggered = True
                    break
            if not triggered and rule.get("sources"):
                if source in [s.lower() for s in rule["sources"]]:
                    triggered = True
            if triggered:
                notifications.append({
                    "rule": rule["name"],
                    "article": article.get("title", ""),
                    "priority": rule["priority"],
                })
        self.pending.extend(notifications)
        return notifications

    def get_pending(self):
        """get and clear pending notifications."""
        pending = list(self.pending)
        self.history.extend(pending)
        self.pending.clear()
        return pending

    def disable_rule(self, name):
        """disable a notification rule."""
        for rule in self.rules:
            if rule["name"] == name:
                rule["active"] = False
                self._save_rules()
                return True
        return False

    def _load_rules(self):
        if os.path.isfile(self.config_path):
            with open(self.config_path) as f:
                return json.load(f)
        return []

    def _save_rules(self):
        with open(self.config_path, "w") as f:
            json.dump(self.rules, f, indent=2)


if __name__ == "__main__":
    nm = NotificationManager("/tmp/test_notif.json")
    nm.add_rule("python_news", keywords=["python", "cpython"],
                priority="high")
    nm.add_rule("security", keywords=["vulnerability", "exploit", "cve"])
    article = {
        "title": "new python 3.11 vulnerability discovered",
        "source": "hackernews",
        "text": "a critical cve was found in cpython",
    }
    alerts = nm.check_article(article)
    print(f"triggered: {len(alerts)} notifications")
    for a in alerts:
        print(f"  [{a['priority']}] {a['rule']}: {a['article']}")
