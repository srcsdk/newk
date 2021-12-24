#!/usr/bin/env python3
"""feed api endpoint for external integration"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


FEEDS_FILE = os.path.join(os.path.dirname(__file__), "feeds.json")
API_PORT = 8085


def load_feeds():
    """load feeds data."""
    if os.path.exists(FEEDS_FILE):
        with open(FEEDS_FILE, "r") as f:
            return json.load(f)
    return []


class FeedAPIHandler(BaseHTTPRequestHandler):
    """simple http handler for feed api."""

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        if path == "/api/feeds":
            self._handle_feeds(params)
        elif path == "/api/articles":
            self._handle_articles(params)
        elif path == "/api/health":
            self._respond(200, {"status": "ok"})
        else:
            self._respond(404, {"error": "not found"})

    def _handle_feeds(self, params):
        feeds = load_feeds()
        category = params.get("category", [None])[0]
        if category:
            feeds = [f for f in feeds if f.get("category") == category]
        self._respond(200, {"feeds": feeds, "total": len(feeds)})

    def _handle_articles(self, params):
        feeds = load_feeds()
        limit = int(params.get("limit", [20])[0])
        articles = []
        for feed in feeds:
            articles.extend(feed.get("articles", []))
        articles.sort(key=lambda a: a.get("date", ""), reverse=True)
        self._respond(200, {"articles": articles[:limit]})

    def _respond(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass


def run_server(port=API_PORT):
    """start the feed api server."""
    server = HTTPServer(("", port), FeedAPIHandler)
    print(f"feed api running on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
