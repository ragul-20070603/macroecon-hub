import requests
import feedparser
import hashlib
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from config import NEWS_API_KEY, RSS_FEEDS, NEWS_KEYWORDS

NEWS_API_BASE = "https://newsapi.org/v2/everything"

def hash_url(url):
    return hashlib.md5(url.encode()).hexdigest()

def fetch_newsapi():
    articles = []
    for keyword in NEWS_KEYWORDS[:5]:
        try:
            params = {
                "q": keyword,
                "apiKey": NEWS_API_KEY,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10
            }
            response = requests.get(NEWS_API_BASE, params=params)
            data = response.json()
            for article in data.get("articles", []):
                if article.get("content") and article.get("url"):
                    articles.append({
                        "url": article["url"],
                        "url_hash": hash_url(article["url"]),
                        "title": article["title"],
                        "content": article.get("content", "") + " " + article.get("description", ""),
                        "source": article["source"]["name"],
                        "published_at": article["publishedAt"],
                        "topic": keyword,
                        "type": "news"
                    })
        except Exception as e:
            print(f"NewsAPI failed for {keyword}: {e}")
    return articles

def fetch_rss():
    articles = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                url = entry.get("link", "")
                content = entry.get("summary", "") or entry.get("description", "")
                if url and content:
                    articles.append({
                        "url": url,
                        "url_hash": hash_url(url),
                        "title": entry.get("title", ""),
                        "content": content,
                        "source": feed.feed.get("title", feed_url),
                        "published_at": entry.get("published", datetime.utcnow().isoformat()),
                        "topic": "general",
                        "type": "rss"
                    })
        except Exception as e:
            print(f"RSS failed for {feed_url}: {e}")
    return articles

def fetch_alpha_vantage_news():
    from config import ALPHA_VANTAGE_API_KEY
    articles = []
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "NEWS_SENTIMENT",
            "topics": "economy_macro,finance",
            "apikey": ALPHA_VANTAGE_API_KEY,
            "limit": 20
        }
        response = requests.get(url, params=params)
        data = response.json()
        for item in data.get("feed", []):
            articles.append({
                "url": item["url"],
                "url_hash": hash_url(item["url"]),
                "title": item["title"],
                "content": item.get("summary", ""),
                "source": item.get("source", "AlphaVantage"),
                "published_at": item.get("time_published", datetime.utcnow().isoformat()),
                "topic": "markets",
                "type": "news"
            })
    except Exception as e:
        print(f"Alpha Vantage news failed: {e}")
    return articles

def fetch_all_news():
    articles = []
    articles.extend(fetch_newsapi())
    articles.extend(fetch_rss())
    articles.extend(fetch_alpha_vantage_news())
    seen = set()
    deduped = []
    for a in articles:
        if a["url_hash"] not in seen:
            seen.add(a["url_hash"])
            deduped.append(a)
    print(f"Fetched {len(deduped)} unique articles")
    return deduped
