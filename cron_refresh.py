#!/usr/bin/env python3
"""scheduled feed refresh with cron-style intervals"""

import time
import threading


class RefreshScheduler:
    """schedule periodic feed refreshes."""

    def __init__(self):
        self.schedules = {}
        self.running = False
        self._thread = None

    def add_feed(self, url, interval_minutes=30, callback=None):
        """schedule a feed for periodic refresh."""
        self.schedules[url] = {
            "interval": interval_minutes * 60,
            "last_refresh": 0,
            "callback": callback,
            "refresh_count": 0,
        }

    def remove_feed(self, url):
        """remove a feed from schedule."""
        self.schedules.pop(url, None)

    def check_due(self):
        """check which feeds are due for refresh."""
        now = time.time()
        due = []
        for url, info in self.schedules.items():
            if now - info["last_refresh"] >= info["interval"]:
                due.append(url)
        return due

    def refresh_feed(self, url):
        """mark feed as refreshed and run callback."""
        if url in self.schedules:
            self.schedules[url]["last_refresh"] = time.time()
            self.schedules[url]["refresh_count"] += 1
            callback = self.schedules[url].get("callback")
            if callback:
                callback(url)

    def run_cycle(self):
        """run one refresh cycle for all due feeds."""
        due = self.check_due()
        for url in due:
            self.refresh_feed(url)
        return due

    def start(self, check_interval=60):
        """start background refresh loop."""
        self.running = True

        def loop():
            while self.running:
                self.run_cycle()
                time.sleep(check_interval)

        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()

    def stop(self):
        """stop background refresh loop."""
        self.running = False

    def status(self):
        """get schedule status for all feeds."""
        now = time.time()
        return {
            url: {
                "interval_min": info["interval"] // 60,
                "last_refresh_ago": round((now - info["last_refresh"]) / 60, 1)
                if info["last_refresh"] > 0 else "never",
                "refresh_count": info["refresh_count"],
            }
            for url, info in self.schedules.items()
        }


if __name__ == "__main__":
    scheduler = RefreshScheduler()
    scheduler.add_feed("https://example.com/feed.xml", interval_minutes=15)
    scheduler.add_feed("https://arxiv.org/rss/cs.AI", interval_minutes=60)
    due = scheduler.run_cycle()
    print(f"refreshed: {len(due)} feeds")
    status = scheduler.status()
    for url, info in status.items():
        print(f"  {url}: every {info['interval_min']}min")
