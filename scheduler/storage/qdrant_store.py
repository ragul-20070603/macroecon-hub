from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import uuid
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION, EMBEDDING_DIM

_client = None

def get_client():
    global _client
    if _client is None:
        _client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return _client

def ensure_collection():
    from qdrant_client.models import PayloadSchemaType
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]
    if QDRANT_COLLECTION not in existing:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
        )
        print(f"Created Qdrant collection: {QDRANT_COLLECTION}")
    try:
        client.create_payload_index(
            collection_name=QDRANT_COLLECTION,
            field_name="status",
            field_schema=PayloadSchemaType.KEYWORD
        )
        print("Created status index")
    except Exception:
        pass

def upsert_chunks(chunks, embeddings):
    client = get_client()
    points = []
    for chunk, embedding in zip(chunks, embeddings):
        points.append(PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk["chunk_id"])),
            vector=embedding,
            payload=chunk
        ))
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)
    print(f"Upserted {len(points)} chunks to Qdrant")

def search(query_embedding, top_k=5, status_filter=None):
    client = get_client()
    query_filter = None
    if status_filter:
        query_filter = Filter(
            must=[FieldCondition(key="status", match=MatchValue(value=status_filter))]
        )
    results = client.query_points(
    collection_name=QDRANT_COLLECTION,
    query=query_embedding,
    limit=top_k,
    query_filter=query_filter,
    with_payload=True
    ).points
    return results

def get_all_hashes():
    client = get_client()
    hashes = set()
    offset = None
    while True:
        result, offset = client.scroll(
            collection_name=QDRANT_COLLECTION,
            scroll_filter=None,
            limit=1000,
            offset=offset,
            with_payload=["url_hash"]
        )
        for point in result:
            hashes.add(point.payload.get("url_hash"))
        if offset is None:
            break
    return hashes

def update_status(chunk_ids, new_status):
    client = get_client()
    for chunk_id in chunk_ids:
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))
        client.set_payload(
            collection_name=QDRANT_COLLECTION,
            payload={"status": new_status},
            points=[point_id]
        )
