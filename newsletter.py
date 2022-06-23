#!/usr/bin/env python3
"""newsletter subscription and aggregation"""

import json
import os
import hashlib
import time


class NewsletterManager:
    """manage newsletter subscriptions."""

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.newk")
        self.data_dir = data_dir
        self.subs_file = os.path.join(data_dir, "newsletters.json")
        os.makedirs(data_dir, exist_ok=True)
        self.subscriptions = self._load()

    def _load(self):
        if os.path.isfile(self.subs_file):
            with open(self.subs_file) as f:
                return json.load(f)
        return []

    def _save(self):
        with open(self.subs_file, "w") as f:
            json.dump(self.subscriptions, f, indent=2)

    def subscribe(self, name, url, category="general"):
        """add a newsletter subscription."""
        sub_id = hashlib.md5(url.encode()).hexdigest()[:10]
        for sub in self.subscriptions:
            if sub["url"] == url:
                return sub
        sub = {
            "id": sub_id,
            "name": name,
            "url": url,
            "category": category,
            "added": time.strftime("%Y-%m-%d"),
            "active": True,
            "issues": [],
        }
        self.subscriptions.append(sub)
        self._save()
        return sub

    def unsubscribe(self, sub_id):
        """remove a subscription."""
        self.subscriptions = [s for s in self.subscriptions if s["id"] != sub_id]
        self._save()

    def add_issue(self, sub_id, title, content_url):
        """record a new issue of a newsletter."""
        for sub in self.subscriptions:
            if sub["id"] == sub_id:
                sub["issues"].append({
                    "title": title,
                    "url": content_url,
                    "date": time.strftime("%Y-%m-%d"),
                    "read": False,
                })
                self._save()
                return True
        return False

    def unread_issues(self):
        """get all unread newsletter issues."""
        unread = []
        for sub in self.subscriptions:
            for issue in sub.get("issues", []):
                if not issue.get("read"):
                    unread.append({
                        "newsletter": sub["name"],
                        "title": issue["title"],
                        "url": issue["url"],
                        "date": issue["date"],
                    })
        unread.sort(key=lambda x: x["date"], reverse=True)
        return unread

    def list_subscriptions(self):
        """list all subscriptions."""
        return [
            {
                "id": s["id"],
                "name": s["name"],
                "category": s["category"],
                "issues": len(s.get("issues", [])),
                "active": s.get("active", True),
            }
            for s in self.subscriptions
        ]


if __name__ == "__main__":
    nm = NewsletterManager("/tmp/newk_newsletters")
    nm.subscribe("python weekly", "https://pythonweekly.com", "programming")
    nm.subscribe("hacker newsletter", "https://hackernewsletter.com", "tech")
    print(f"subscriptions: {len(nm.list_subscriptions())}")
    for sub in nm.list_subscriptions():
        print(f"  {sub['name']} ({sub['category']})")
