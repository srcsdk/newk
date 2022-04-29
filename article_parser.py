#!/usr/bin/env python3
"""parse and extract article content from web pages"""

import re


def extract_title(html):
    """extract article title from html."""
    patterns = [
        r"<h1[^>]*>(.*?)</h1>",
        r"<title>(.*?)</title>",
        r'property="og:title"\s+content="([^"]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if match:
            return _clean_text(match.group(1))
    return ""


def extract_body(html):
    """extract main article body text."""
    html = re.sub(
        r"<(script|style|nav|header|footer)[^>]*>.*?</\1>",
        "", html, flags=re.DOTALL | re.IGNORECASE,
    )
    article_match = re.search(
        r"<article[^>]*>(.*?)</article>",
        html, re.DOTALL | re.IGNORECASE,
    )
    if article_match:
        html = article_match.group(1)
    paragraphs = re.findall(
        r"<p[^>]*>(.*?)</p>", html, re.DOTALL | re.IGNORECASE,
    )
    texts = [_clean_text(p) for p in paragraphs]
    return "\n\n".join(t for t in texts if len(t) > 20)


def extract_metadata(html):
    """extract article metadata."""
    metadata = {}
    author_match = re.search(
        r'name="author"\s+content="([^"]+)"', html, re.IGNORECASE,
    )
    if author_match:
        metadata["author"] = author_match.group(1)
    date_match = re.search(
        r'property="article:published_time"\s+content="([^"]+)"',
        html, re.IGNORECASE,
    )
    if date_match:
        metadata["published"] = date_match.group(1)
    desc_match = re.search(
        r'name="description"\s+content="([^"]+)"',
        html, re.IGNORECASE,
    )
    if desc_match:
        metadata["description"] = desc_match.group(1)
    return metadata


def extract_images(html):
    """extract image urls from article."""
    pattern = r'<img[^>]+src="([^"]+)"'
    images = re.findall(pattern, html, re.IGNORECASE)
    return [img for img in images if not _is_tracking_pixel(img)]


def _is_tracking_pixel(url):
    """check if image url is likely a tracking pixel."""
    indicators = ["1x1", "pixel", "tracking", "beacon", "spacer"]
    return any(ind in url.lower() for ind in indicators)


def _clean_text(text):
    """clean html text by removing tags and extra whitespace."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&\w+;", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def word_count(text):
    """count words in text."""
    return len(text.split())


def reading_time(text, wpm=200):
    """estimate reading time in minutes."""
    words = word_count(text)
    return max(1, round(words / wpm))


if __name__ == "__main__":
    sample = """
    <html><head><title>test article</title></head>
    <body><article>
    <h1>sample heading</h1>
    <p>this is the first paragraph of the article content.</p>
    <p>this is the second paragraph with more details about the topic.</p>
    </article></body></html>
    """
    title = extract_title(sample)
    body = extract_body(sample)
    print(f"title: {title}")
    print(f"body length: {len(body)} chars")
    print(f"reading time: {reading_time(body)} min")
