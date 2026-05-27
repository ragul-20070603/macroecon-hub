from supabase import create_client
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from config import SUPABASE_URL, SUPABASE_KEY

_client = None

def get_client():
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client

def store_timeseries(indicator_name, source, records):
    client = get_client()
    rows = []
    for r in records:
        rows.append({
            "indicator": indicator_name,
            "source": source,
            "country": r.get("country", "US"),
            "date": r.get("date") or str(r.get("year", "")),
            "value": float(r["value"])
        })
    if rows:
        client.table("timeseries").upsert(rows, on_conflict="indicator,source,country,date").execute()
        print(f"Stored {len(rows)} timeseries rows for {indicator_name}")

def get_timeseries(indicator_name, country="US", start_year=None, end_year=None):
    client = get_client()
    query = client.table("timeseries").select("*").eq("indicator", indicator_name).eq("country", country)
    if start_year:
        query = query.gte("date", f"{start_year}-01-01")
    if end_year:
        query = query.lte("date", f"{end_year}-12-31")
    result = query.order("date").execute()
    return result.data

def store_warm_chunk(chunk):
    client = get_client()
    client.table("warm_chunks").upsert(chunk, on_conflict="chunk_id").execute()

def get_warm_chunks_for_query(query_embedding_str, top_k=5):
    client = get_client()
    result = client.table("warm_chunks").select("*").eq("status", "stale").limit(200).execute()
    return result.data

def store_url_hash(url_hash):
    client = get_client()
    client.table("url_hashes").upsert({"hash": url_hash}).execute()

def get_all_url_hashes():
    client = get_client()
    result = client.table("url_hashes").select("hash").execute()
    return {row["hash"] for row in result.data}
