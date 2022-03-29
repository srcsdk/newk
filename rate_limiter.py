#!/usr/bin/env python3
"""api rate limiter for feed fetching"""

import time
import threading


class RateLimiter:
    """rate limit api requests per domain."""

    def __init__(self, requests_per_minute=30):
        self.rpm = requests_per_minute
        self.interval = 60.0 / requests_per_minute
        self.timestamps = {}
        self.lock = threading.Lock()

    def acquire(self, domain):
        """wait if necessary to respect rate limit for domain."""
        with self.lock:
            now = time.time()
            last = self.timestamps.get(domain, 0)
            wait = self.interval - (now - last)
            if wait > 0:
                time.sleep(wait)
            self.timestamps[domain] = time.time()

    def can_request(self, domain):
        """check if a request can be made without waiting."""
        now = time.time()
        last = self.timestamps.get(domain, 0)
        return (now - last) >= self.interval

    def reset(self, domain=None):
        """reset rate limit tracking."""
        with self.lock:
            if domain:
                self.timestamps.pop(domain, None)
            else:
                self.timestamps.clear()

    def status(self):
        """get rate limiter status."""
        now = time.time()
        return {
            domain: {
                "last_request": round(now - ts, 1),
                "can_request": (now - ts) >= self.interval,
            }
            for domain, ts in self.timestamps.items()
        }


if __name__ == "__main__":
    limiter = RateLimiter(requests_per_minute=60)
    limiter.acquire("example.com")
    print(f"can request: {limiter.can_request('example.com')}")
    time.sleep(1.1)
    print(f"after wait: {limiter.can_request('example.com')}")
    print(f"status: {limiter.status()}")
