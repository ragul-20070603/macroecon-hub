import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from config import GROQ_API_KEY, GROQ_MODEL
from groq import Groq

def get_client():
    return Groq(api_key=GROQ_API_KEY)

def generate_answer(query, context_chunks, sources, timeseries_context=None, query_type="conceptual"):
    client = get_client()
    context = "\n\n".join(context_chunks) if context_chunks else ""

    ts_section = ""
    if timeseries_context:
        ts_section = f"\n\nHistorical Time-Series Data:\n{timeseries_context}"

    system_prompt = """You are a macroeconomics expert assistant with access to real-time news, 
historical economic data, and comprehensive knowledge of global economics.
Always cite your sources. Be precise with numbers when data is available.
If asked about trends, describe them clearly. Never hallucinate statistics."""

    user_prompt = f"""Context from knowledge base:
{context}
{ts_section}

Question: {query}

Provide a comprehensive, accurate answer. If numerical data is available, use it precisely.
If discussing trends, reference the actual data points. Always indicate data sources."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=8000
    )
    return response.choices[0].message.content

def generate_trend_narrative(query, trend_summary, indicator, country):
    client = get_client()
    prompt = f"""Based on this economic data for {indicator} in {country}:
- Period: {trend_summary['start_date']} to {trend_summary['end_date']}
- Starting value: {trend_summary['start_value']:.2f}
- Current value: {trend_summary['end_value']:.2f}
- Minimum: {trend_summary['min_value']:.2f}
- Maximum: {trend_summary['max_value']:.2f}
- Average: {trend_summary['average']:.2f}

User question: {query}

Provide a detailed economic analysis of this trend, explaining key turning points, 
causes, and implications. Be specific about historical events that caused major changes."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=6000
    )
    return response.choices[0].message.content
