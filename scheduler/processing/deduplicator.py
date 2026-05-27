import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from config import SIMILARITY_THRESHOLD

def url_dedup(articles, existing_hashes):
    return [a for a in articles if a["url_hash"] not in existing_hashes]

def semantic_dedup(chunks, collection):
    from scheduler.processing.embedder import embed_query
    unique = []
    for chunk in chunks:
        try:
            embedding = embed_query(chunk["text"])
            results = collection.query(
                query_embeddings=[embedding],
                n_results=1
            )
            if results["distances"] and results["distances"][0]:
                similarity = 1 - results["distances"][0][0]
                if similarity >= SIMILARITY_THRESHOLD:
                    continue
        except Exception:
            pass
        unique.append(chunk)
    return unique
