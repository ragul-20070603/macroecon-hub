import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from config import FRED_API_KEY, FRED_SERIES

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

def fetch_series(series_id, start_date="1947-01-01"):
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start_date,
        "sort_order": "asc"
    }
    response = requests.get(FRED_BASE, params=params)
    data = response.json()
    observations = data.get("observations", [])
    results = []
    for obs in observations:
        if obs["value"] != ".":
            results.append({
                "date": obs["date"],
                "value": float(obs["value"])
            })
    return results

def fetch_all_series():
    all_data = {}
    for name, series_id in FRED_SERIES.items():
        print(f"Fetching FRED series: {name} ({series_id})")
        try:
            all_data[name] = fetch_series(series_id)
            print(f"Got {len(all_data[name])} observations for {name}")
        except Exception as e:
            print(f"Failed to fetch {name}: {e}")
    return all_data

def fetch_latest(series_id):
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1
    }
    response = requests.get(FRED_BASE, params=params)
    data = response.json()
    obs = data.get("observations", [])
    if obs and obs[0]["value"] != ".":
        return {"date": obs[0]["date"], "value": float(obs[0]["value"])}
    return None
