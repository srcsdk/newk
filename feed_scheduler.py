#!/usr/bin/env python3
"""schedule feed refresh intervals"""

import json
import os
import time


class FeedScheduler:
    """manage feed refresh schedules."""

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.newk")
        self.data_dir = data_dir
        self.schedule_file = os.path.join(data_dir, "schedule.json")
        os.makedirs(data_dir, exist_ok=True)
        self.schedules = self._load()

    def _load(self):
        if os.path.isfile(self.schedule_file):
            with open(self.schedule_file) as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(self.schedule_file, "w") as f:
            json.dump(self.schedules, f, indent=2)

    def set_interval(self, feed_url, minutes):
        """set refresh interval for a feed."""
        self.schedules[feed_url] = {
            "interval": minutes,
            "last_refresh": self.schedules.get(feed_url, {}).get("last_refresh", 0),
        }
        self._save()

    def mark_refreshed(self, feed_url):
        """mark a feed as just refreshed."""
        if feed_url in self.schedules:
            self.schedules[feed_url]["last_refresh"] = time.time()
            self._save()

    def needs_refresh(self, feed_url):
        """check if a feed needs refreshing."""
        schedule = self.schedules.get(feed_url)
        if not schedule:
            return True
        interval = schedule.get("interval", 30) * 60
        last = schedule.get("last_refresh", 0)
        return (time.time() - last) >= interval

    def due_feeds(self):
        """get all feeds that are due for refresh."""
        due = []
        for url, schedule in self.schedules.items():
            if self.needs_refresh(url):
                due.append({
                    "url": url,
                    "interval": schedule.get("interval", 30),
                    "overdue_minutes": round(
                        (time.time() - schedule.get("last_refresh", 0)) / 60, 1
                    ),
                })
        due.sort(key=lambda d: d["overdue_minutes"], reverse=True)
        return due

    def status(self):
        """get scheduler status."""
        total = len(self.schedules)
        due = len(self.due_feeds())
        return {"total_feeds": total, "due_for_refresh": due}


if __name__ == "__main__":
    sched = FeedScheduler("/tmp/newk_sched")
    sched.set_interval("https://hnrss.org/frontpage", 15)
    sched.set_interval("https://lobste.rs/rss", 30)
    print(f"status: {sched.status()}")
    due = sched.due_feeds()
    print(f"due for refresh: {len(due)}")
    for d in due:
        print(f"  {d['url']} (every {d['interval']}m)")
