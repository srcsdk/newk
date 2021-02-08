from setuptools import setup

setup(
    name="newk",
    version="0.1.0",
    author="srcsdk",
    author_email="srcsdk@users.noreply.github.com",
    description="feed aggregator and news reader",
    url="https://github.com/srcsdk/newk",
    py_modules=[
        "api_feeds",
        "preview",
        "quality",
        "rss_parser",
        "scheduler",
        "scrape",
        "tags",
        "validate",
    ],
    python_requires=">=3.8",
    install_requires=[
        "feedparser",
        "requests",
        "beautifulsoup4",
        "lxml",
    ],
    entry_points={
        "console_scripts": [
            "newk=rss_parser:main",
            "newk-scrape=scrape:main",
            "newk-feeds=api_feeds:main",
        ],
    },
)
