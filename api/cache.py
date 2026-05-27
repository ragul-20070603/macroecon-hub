import hashlib
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import UPSTASH_REDIS_URL, UPSTASH_REDIS_TOKEN, CACHE_TTL_SECONDS
import requests

def _cache_key(query):
    return "query:" + hashlib.md5(query.lower().strip().encode()).hexdigest()

def get_cached(query):
    try:
        key = _cache_key(query)
        url = f"{UPSTASH_REDIS_URL}/get/{key}"
        headers = {"Authorization": f"Bearer {UPSTASH_REDIS_TOKEN}"}
        response = requests.get(url, headers=headers)
        data = response.json()
        if data.get("result"):
            return json.loads(data["result"])
    except Exception:
        pass
    return None

def set_cached(query, result):
    try:
        key = _cache_key(query)
        url = f"{UPSTASH_REDIS_URL}/set/{key}"
        headers = {"Authorization": f"Bearer {UPSTASH_REDIS_TOKEN}"}
        payload = {"value": json.dumps(result), "ex": CACHE_TTL_SECONDS}
        requests.post(url, headers=headers, json=payload)
    except Exception:
        pass
