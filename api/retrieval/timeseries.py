import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from scheduler.storage.supabase_store import get_timeseries

def get_indicator_data(indicator, country="US", start_year=None, end_year=None):
    records = get_timeseries(indicator, country, start_year, end_year)
    return records

def format_timeseries_for_llm(records, indicator, country):
    if not records:
        return f"No data found for {indicator} in {country}."
    lines = [f"{r['date'][:4]}: {r['value']:.2f}" for r in records]
    summary = "\n".join(lines)
    return f"{indicator.upper()} data for {country}:\n{summary}"

def get_trend_summary(records):
    if len(records) < 2:
        return {}
    values = [r["value"] for r in records]
    dates = [r["date"] for r in records]
    return {
        "start_date": dates[0],
        "end_date": dates[-1],
        "start_value": values[0],
        "end_value": values[-1],
        "min_value": min(values),
        "max_value": max(values),
        "average": sum(values) / len(values),
        "total_records": len(records),
        "dates": dates,
        "values": values
    }
