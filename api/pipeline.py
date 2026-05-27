import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.retrieval.classifier import classify_query, extract_years, extract_indicator, extract_country
from api.retrieval.retriever import retrieve_conceptual, retrieve_news, retrieve_historical
from api.retrieval.timeseries import get_indicator_data, format_timeseries_for_llm, get_trend_summary
from api.generation.generator import generate_answer, generate_trend_narrative
from api.cache import get_cached, set_cached

def run_pipeline(query):
    cached = get_cached(query)
    if cached:
        cached["from_cache"] = True
        return cached

    query_type = classify_query(query)
    years = extract_years(query)
    indicator = extract_indicator(query)
    country = extract_country(query)

    start_year = min(years) if years else None
    end_year = max(years) if years else None

    chunks = []
    sources = []
    timeseries_context = None
    trend_data = None

    if query_type == "timeseries":
        records = get_indicator_data(indicator, country, start_year, end_year)
        if records:
            timeseries_context = format_timeseries_for_llm(records, indicator, country)
            trend_data = get_trend_summary(records)
        chunks, sources = retrieve_conceptual(query)
        answer = generate_answer(query, chunks, sources, timeseries_context, query_type)
        if trend_data:
            narrative = generate_trend_narrative(query, trend_data, indicator, country)
            answer = answer + "\n\n**Trend Analysis:**\n" + narrative

    elif query_type == "news":
        chunks, sources = retrieve_news(query)
        answer = generate_answer(query, chunks, sources, None, query_type)

    elif query_type == "historical":
        chunks, sources = retrieve_historical(query)
        records = get_indicator_data(indicator, country, start_year, end_year)
        if records:
            timeseries_context = format_timeseries_for_llm(records, indicator, country)
        answer = generate_answer(query, chunks, sources, timeseries_context, query_type)

    else:
        chunks, sources = retrieve_conceptual(query)
        answer = generate_answer(query, chunks, sources, None, query_type)

    result = {
        "answer": answer,
        "sources": list(set(sources)),
        "query_type": query_type,
        "indicator": indicator,
        "country": country,
        "trend_data": trend_data,
        "from_cache": False
    }

    set_cached(query, result)
    return result
