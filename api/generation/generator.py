
import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../..")
    ),
)

from config import GROQ_API_KEY, GROQ_MODEL
from groq import Groq


def get_client():
    return Groq(api_key=GROQ_API_KEY)


def generate_answer(
    query,
    context_chunks,
    sources,
    timeseries_context=None,
    query_type="conceptual",
):
    client = get_client()

    context = "\n\n".join(
        str(chunk) for chunk in context_chunks
    ) if context_chunks else "No additional context available."

    ts_section = ""

    if timeseries_context:
        ts_section = (
            "\n\nHistorical Time-Series Data:\n"
            f"{timeseries_context}"
        )

    system_prompt = """
You are a macroeconomics expert assistant with access to
historical economic data, economic research, and news.

Instructions:
- Answer the user's question clearly and accurately.
- Use the supplied context and data whenever relevant.
- Cite sources when they are available.
- Be precise with numerical values and dates.
- Explain economic trends and their implications.
- Never invent statistics or claim that data was verified
  when it was not.
- If the supplied context is insufficient, state the limitation.
"""

    source_context = ""

    if sources:
        source_context = (
            "\n\nAvailable sources:\n"
            + "\n".join(str(source) for source in sources)
        )

    user_prompt = f"""
Query type: {query_type}

Context from the knowledge base:
{context}
{ts_section}
{source_context}

Question:
{query}

Provide a comprehensive, accurate answer.
Use relevant numerical data when available.
Explain important economic concepts and trends clearly.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.3,
        max_tokens=8000,
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError("The language model returned an empty answer.")

    return answer


def generate_trend_narrative(
    query,
    trend_summary,
    indicator,
    country,
):
    client = get_client()

    prompt = f"""
Analyze the following economic time-series data.

Indicator: {indicator}
Country: {country}
Period: {trend_summary['start_date']} to
        {trend_summary['end_date']}

Starting value: {trend_summary['start_value']:.2f}
Ending value: {trend_summary['end_value']:.2f}
Minimum value: {trend_summary['min_value']:.2f}
Maximum value: {trend_summary['max_value']:.2f}
Average value: {trend_summary['average']:.2f}

User question:
{query}

Explain:
1. The overall trend.
2. Important turning points, if supported by the data.
3. Possible economic causes, distinguishing facts from hypotheses.
4. Implications for the economy.

Do not invent historical events or statistics.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert macroeconomic analyst. "
                    "Base your analysis on the supplied data, "
                    "and clearly distinguish evidence from inference."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.3,
        max_tokens=4000,
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError(
            "The language model returned an empty trend analysis."
        )

    return answer
