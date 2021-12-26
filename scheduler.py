#!/usr/bin/env python3
"""schedule periodic feed refreshes and cache updates"""

import json
import os
import sys
import time
from datetime import datetime


CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scrape_cache.json")
SCHEDULE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schedule.json")

DEFAULT_INTERVAL = 3600  # 1 hour


def load_schedule():
    """load refresh schedule from config"""
    if not os.path.exists(SCHEDULE_FILE):
        return {"interval": DEFAULT_INTERVAL, "last_run": None}
    try:
        with open(SCHEDULE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {"interval": DEFAULT_INTERVAL, "last_run": None}


def save_schedule(schedule):
    """save schedule state"""
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedule, f, indent=2)


def needs_refresh(schedule):
    """check if feeds need refreshing based on schedule"""
    last_run = schedule.get("last_run")
    if not last_run:
        return True

    interval = schedule.get("interval", DEFAULT_INTERVAL)
    try:
        last_time = datetime.fromisoformat(last_run)
        elapsed = (datetime.now() - last_time).total_seconds()
        return elapsed >= interval
    except (ValueError, TypeError):
        return True


def run_refresh():
    """run the scraper and update cache"""
    try:
        from scrape import scrape_all, save_cache
        print(f"[{datetime.now().strftime('%H:%M:%S')}] refreshing feeds...")
        items = scrape_all(verbose=False)
        save_cache(items)
        print(f"  cached {len(items)} items")
        return len(items)
    except ImportError:
        print("scrape module not found", file=sys.stderr)
        return 0


def run_scheduler(interval=None):
    """run continuous refresh loop"""
    schedule = load_schedule()
    if interval:
        schedule["interval"] = interval

    print(f"feed scheduler started (interval: {schedule['interval']}s)")
    print("ctrl+c to stop\n")

    try:
        while True:
            if needs_refresh(schedule):
                run_refresh()
                schedule["last_run"] = datetime.now().isoformat()
                save_schedule(schedule)
            else:
                remaining = schedule["interval"]
                print(f"  next refresh in {remaining}s")

            time.sleep(min(schedule["interval"], 60))
    except KeyboardInterrupt:
        print("\nscheduler stopped")
        save_schedule(schedule)


if __name__ == "__main__":
    interval = None
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            print("usage: python scheduler.py [interval_seconds]")
            sys.exit(1)

    run_scheduler(interval)
