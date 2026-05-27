import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from config import TOP_K
from scheduler.processing.embedder import embed_query
from scheduler.storage.qdrant_store import search, ensure_collection
from scheduler.storage.supabase_store import get_warm_chunks_for_query
from datetime import datetime

def compute_recency_score(ingested_at):
    try:
        ingested = datetime.fromisoformat(ingested_at)
        days_old = (datetime.utcnow() - ingested).days
        return 1 / (1 + days_old)
    except Exception:
        return 0.1

def rerank(results, alpha=0.7):
    scored = []
    for r in results:
        semantic_score = r.score if hasattr(r, 'score') else r.get("score", 0.5)
        ingested_at = r.payload.get("ingested_at", "") if hasattr(r, 'payload') else r.get("ingested_at", "")
        recency = compute_recency_score(ingested_at)
        final_score = alpha * semantic_score + (1 - alpha) * recency
        scored.append((final_score, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored]

def retrieve_conceptual(query, top_k=TOP_K):
    ensure_collection()
    embedding = embed_query(query)
    results = search(embedding, top_k=top_k * 2, status_filter="active")
    reranked = rerank(results)[:top_k]
    chunks = [r.payload.get("text", "") for r in reranked]
    sources = [r.payload.get("source", "") for r in reranked]
    return chunks, sources

def retrieve_news(query, top_k=TOP_K):
    ensure_collection()
    embedding = embed_query(query)
    results = search(embedding, top_k=top_k * 2, status_filter="active")
    news_results = [r for r in results if r.payload.get("type") in ("news", "rss")]
    reranked = rerank(news_results)[:top_k]
    if len(reranked) < top_k:
        reranked = rerank(results)[:top_k]
    chunks = [r.payload.get("text", "") for r in reranked]
    sources = [r.payload.get("source", "") for r in reranked]
    return chunks, sources

def retrieve_historical(query, top_k=TOP_K):
    ensure_collection()
    embedding = embed_query(query)
    active_results = search(embedding, top_k=top_k, status_filter="active")
    stale_results = search(embedding, top_k=top_k, status_filter="stale")
    archived_results = search(embedding, top_k=top_k, status_filter="archived")
    all_results = list(active_results) + list(stale_results) + list(archived_results)
    reranked = rerank(all_results)[:top_k]
    chunks = [r.payload.get("text", "") for r in reranked]
    sources = [r.payload.get("source", "") for r in reranked]
    return chunks, sources
