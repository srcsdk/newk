#!/usr/bin/env python3
"""monitor feed health and availability"""

import time
from urllib.request import urlopen, Request
from urllib.error import URLError


class FeedHealthMonitor:
    """track feed availability and response times."""

    def __init__(self):
        self.history = {}

    def check(self, feed_url):
        """check if a feed is healthy."""
        start = time.time()
        try:
            req = Request(feed_url, headers={"User-Agent": "newk/1.0"})
            resp = urlopen(req, timeout=10)
            status = resp.getcode()
            elapsed = time.time() - start
            result = {
                "url": feed_url,
                "status": status,
                "response_time": round(elapsed, 3),
                "healthy": 200 <= status < 400,
                "checked_at": time.strftime("%Y-%m-%d %H:%M"),
            }
        except URLError as e:
            result = {
                "url": feed_url,
                "status": 0,
                "error": str(e),
                "healthy": False,
                "checked_at": time.strftime("%Y-%m-%d %H:%M"),
            }
        self.history.setdefault(feed_url, []).append(result)
        if len(self.history[feed_url]) > 100:
            self.history[feed_url] = self.history[feed_url][-100:]
        return result

    def uptime(self, feed_url):
        """calculate uptime percentage for a feed."""
        checks = self.history.get(feed_url, [])
        if not checks:
            return 0
        healthy = sum(1 for c in checks if c.get("healthy"))
        return round(healthy / len(checks) * 100, 1)

    def avg_response_time(self, feed_url):
        """average response time for a feed."""
        checks = self.history.get(feed_url, [])
        times = [c["response_time"] for c in checks if "response_time" in c]
        if not times:
            return 0
        return round(sum(times) / len(times), 3)

    def report(self):
        """generate health report for all monitored feeds."""
        report = []
        for url, checks in self.history.items():
            report.append({
                "url": url,
                "checks": len(checks),
                "uptime": self.uptime(url),
                "avg_response": self.avg_response_time(url),
                "last_status": checks[-1].get("healthy") if checks else None,
            })
        report.sort(key=lambda r: r["uptime"])
        return report


if __name__ == "__main__":
    monitor = FeedHealthMonitor()
    print("feed health monitor ready")
    print("usage: monitor.check(url) to check a feed")
