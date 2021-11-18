#!/usr/bin/env python3
"""feed backup and restore with json serialization"""

import json
import os
import time
from datetime import datetime


BACKUP_DIR = os.path.join(os.path.dirname(__file__), "backups")


def create_backup(feeds, preferences, name=None):
    """create a backup of feeds and preferences.

    saves to timestamped json file in backup directory.
    """
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if name is None:
        name = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = {
        "version": 1,
        "timestamp": time.time(),
        "date": datetime.now().isoformat(),
        "feeds": feeds,
        "preferences": preferences,
    }
    path = os.path.join(BACKUP_DIR, f"backup_{name}.json")
    with open(path, "w") as f:
        json.dump(backup, f, indent=2)
    return path


def restore_backup(path):
    """restore feeds and preferences from backup file."""
    with open(path, "r") as f:
        backup = json.load(f)
    return backup.get("feeds", []), backup.get("preferences", {})


def list_backups():
    """list available backups sorted by date."""
    if not os.path.exists(BACKUP_DIR):
        return []
    backups = []
    for filename in os.listdir(BACKUP_DIR):
        if filename.endswith(".json"):
            path = os.path.join(BACKUP_DIR, filename)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                backups.append({
                    "filename": filename,
                    "path": path,
                    "date": data.get("date", "unknown"),
                    "feeds": len(data.get("feeds", [])),
                })
            except (json.JSONDecodeError, OSError):
                continue
    return sorted(backups, key=lambda b: b["date"], reverse=True)


def merge_backup(current_feeds, backup_feeds):
    """merge backup feeds into current, avoiding duplicates."""
    current_urls = {f.get("url") for f in current_feeds}
    new_feeds = [f for f in backup_feeds if f.get("url") not in current_urls]
    return current_feeds + new_feeds


if __name__ == "__main__":
    backups = list_backups()
    print(f"available backups: {len(backups)}")
    for b in backups:
        print(f"  {b['date']} ({b['feeds']} feeds) {b['filename']}")
