from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from config import HOT_TIER_DAYS, WARM_TIER_DAYS
from scheduler.storage.qdrant_store import get_client, QDRANT_COLLECTION, update_status
from scheduler.storage.supabase_store import store_warm_chunk

def migrate_tiers():
    client = get_client()
    now = datetime.utcnow()
    hot_cutoff = (now - timedelta(days=HOT_TIER_DAYS)).isoformat()
    warm_cutoff = (now - timedelta(days=WARM_TIER_DAYS)).isoformat()

    offset = None
    to_stale = []
    to_archive = []

    while True:
        result, offset = client.scroll(
            collection_name=QDRANT_COLLECTION,
            limit=500,
            offset=offset,
            with_payload=True
        )
        for point in result:
            ingested = point.payload.get("ingested_at", "")
            status = point.payload.get("status", "active")
            if ingested < warm_cutoff and status in ("active", "stale"):
                to_archive.append(point)
            elif ingested < hot_cutoff and status == "active":
                to_stale.append(point)
        if offset is None:
            break

    for point in to_stale:
        chunk_id = point.payload.get("chunk_id")
        if chunk_id:
            update_status([chunk_id], "stale")
            store_warm_chunk({**point.payload, "status": "stale"})
    print(f"Migrated {len(to_stale)} chunks to stale")

    for point in to_archive:
        chunk_id = point.payload.get("chunk_id")
        if chunk_id:
            update_status([chunk_id], "archived")
            store_warm_chunk({**point.payload, "status": "archived"})
    print(f"Migrated {len(to_archive)} chunks to archived")
