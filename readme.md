## newk

feed aggregator and news reader. parses rss/atom feeds, scrapes articles, and scores content quality.

### install

```
pip install newk
```

### usage

```
newk
newk-scrape --url https://example.com/feed
newk-feeds
```

```python
from rss_parser import parse_feed
articles = parse_feed("https://example.com/rss")

from scrape import scrape_article
content = scrape_article("https://example.com/article")

from quality import score
rating = score(content)
```
