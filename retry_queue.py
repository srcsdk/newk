#!/usr/bin/env python3
"""feed retry queue for failed fetches with exponential backoff"""

import time
import json
import os


RETRY_FILE = os.path.join(os.path.dirname(__file__), "retry_state.json")


def load_state():
    """load retry state from file."""
    if os.path.exists(RETRY_FILE):
        with open(RETRY_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    """persist retry state."""
    with open(RETRY_FILE, "w") as f:
        json.dump(state, f, indent=2)


def add_to_queue(url, max_retries=5):
    """add a failed url to retry queue."""
    state = load_state()
    if url not in state:
        state[url] = {"retries": 0, "max_retries": max_retries,
                      "last_attempt": 0, "status": "pending"}
    state[url]["retries"] += 1
    state[url]["last_attempt"] = time.time()
    if state[url]["retries"] >= max_retries:
        state[url]["status"] = "dead"
    save_state(state)
    return state[url]


def backoff_delay(retries, base=2, max_delay=3600):
    """calculate exponential backoff delay in seconds."""
    delay = base ** retries
    return min(delay, max_delay)


def get_ready(state=None):
    """get urls ready for retry based on backoff timing."""
    if state is None:
        state = load_state()
    now = time.time()
    ready = []
    for url, info in state.items():
        if info["status"] == "dead":
            continue
        delay = backoff_delay(info["retries"])
        if now - info["last_attempt"] >= delay:
            ready.append(url)
    return ready


def mark_success(url):
    """remove url from retry queue after successful fetch."""
    state = load_state()
    if url in state:
        del state[url]
        save_state(state)


def queue_stats(state=None):
    """get retry queue statistics."""
    if state is None:
        state = load_state()
    pending = sum(1 for v in state.values() if v["status"] == "pending")
    dead = sum(1 for v in state.values() if v["status"] == "dead")
    return {"total": len(state), "pending": pending, "dead": dead}


if __name__ == "__main__":
    print("retry queue stats:", queue_stats())
