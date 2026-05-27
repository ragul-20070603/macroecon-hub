import re
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'==.*?==', '', text)
    text = text.strip()
    return text

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text = clean_text(text)
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c for c in chunks if len(c.strip()) > 50]

def prepare_chunks(article):
    raw_chunks = chunk_text(article["content"])
    prepared = []
    for i, chunk in enumerate(raw_chunks):
        prepared.append({
            "text": chunk,
            "chunk_id": f"{article['url_hash']}_{i}",
            "url_hash": article["url_hash"],
            "url": article.get("url", ""),
            "source": article.get("source", ""),
            "title": article.get("title", ""),
            "topic": article.get("topic", "general"),
            "type": article.get("type", "news"),
            "published_at": article.get("published_at", ""),
            "ingested_at": __import__('datetime').datetime.utcnow().isoformat(),
            "status": "active"
        })
    return prepared
