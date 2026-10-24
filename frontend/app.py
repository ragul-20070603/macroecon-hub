
import streamlit as st
import requests
import plotly.graph_objects as go
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv(
    "API_URL",
    "https://macroecon-hub-api.onrender.com"
).rstrip("/")

st.set_page_config(
    page_title="MacroEcon Hub",
    page_icon="📊",
    layout="wide"
)


def normalize_response(data):
    """
    Normalize API responses when the actual payload is nested
    inside fields such as 'value', 'data', or 'result'.
    """
    for _ in range(5):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return {"answer": data}

        if not isinstance(data, dict):
            return {"answer": str(data)}

        # Already contains the expected response fields.
        if "answer" in data:
            return data

        # Unwrap common API response wrappers.
        unwrapped = False

        for key in ("value", "data", "result"):
            if key in data:
                payload = data[key]

                if isinstance(payload, (dict, str)):
                    data = payload
                    unwrapped = True
                    break

        if not unwrapped:
            return data

    return data if isinstance(data, dict) else {"answer": str(data)}


def display_sources(sources):
    if not sources:
        return

    if isinstance(sources, str):
        sources = [sources]

    if isinstance(sources, list):
        with st.expander("📚 Sources used"):
            for source in sources:
                if source:
                    st.markdown(f"- {source}")


st.title("📊 MacroEcon Hub")
st.markdown(
    "*A live macroeconomic intelligence system — "
    "updated every 30 minutes from global sources*"
)
st.divider()

col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input(
        "Ask anything about macroeconomics:",
        placeholder=(
            "e.g. What was US inflation from 1990 to 2024? "
            "/ What did the Fed announce this week?"
        ),
        key="macro_query",
    )

with col2:
    st.markdown("###")
    ask_btn = st.button(
        "Ask",
        use_container_width=True,
        type="primary",
    )

st.markdown("**Example queries:**")

examples = st.columns(4)

example_queries = [
    "What causes inflation?",
    "US inflation rate trend from 1990 to 2024",
    "What did the Federal Reserve do this week?",
    "Compare GDP growth US vs China",
]

for i, example in enumerate(example_queries):
    with examples[i]:
        if st.button(example, use_container_width=True):
            st.session_state["macro_query"] = example
            st.session_state["run_macro_query"] = True

if st.session_state.pop("run_macro_query", False):
    ask_btn = True
    query = st.session_state["macro_query"]

st.divider()

if ask_btn and query.strip():

    with st.spinner(
        "Searching knowledge base and generating answer... "
        "(first request may take 30–60 seconds)"
    ):
        try:
            response = requests.post(
                f"{API_URL}/query",
                json={"query": query.strip()},
                timeout=120,
            )

            response.raise_for_status()

            try:
                raw_result = response.json()
            except ValueError:
                st.error(
                    "The backend returned an invalid JSON response. "
                    "Please check the API logs."
                )
                st.code(response.text[:3000])
                raw_result = None

            if raw_result is not None:
                result = normalize_response(raw_result)

                if result.get("from_cache"):
                    st.caption("⚡ Cached response")

                st.markdown(
                    "**Query type detected:** "
                    f"`{result.get('query_type', 'conceptual')}`"
                )

                st.markdown("### Answer")

                answer = result.get("answer")

                if answer is not None and str(answer).strip():
                    st.markdown(str(answer))
                else:
                    st.error(
                        "The API responded, but no answer was found. "
                        "The backend response structure needs checking."
                    )
                    with st.expander("Debug API response"):
                        st.json(result)

                # Display trend chart when time-series data is available.
                trend_data = result.get("trend_data")

                if isinstance(trend_data, dict):
                    dates = trend_data.get("dates")
                    values = trend_data.get("values")

                    if (
                        isinstance(dates, list)
                        and isinstance(values, list)
                        and dates
                        and values
                        and len(dates) == len(values)
                    ):
                        st.markdown("### 📈 Trend Chart")

                        fig = go.Figure()

                        fig.add_trace(
                            go.Scatter(
                                x=dates,
                                y=values,
                                mode="lines",
                                name=result.get("indicator", "Value"),
                                line=dict(
                                    color="#1f77b4",
                                    width=2,
                                ),
                            )
                        )

                        fig.update_layout(
                            title=(
                                f"{result.get('indicator', 'Indicator')} "
                                f"— {result.get('country', 'US')}"
                            ),
                            xaxis_title="Date",
                            yaxis_title="Value",
                            hovermode="x unified",
                            height=400,
                        )

                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                        )

                display_sources(result.get("sources"))

        except requests.exceptions.Timeout:
            st.error(
                "Request timed out. The server may be starting up. "
                "Please try again in 30 seconds."
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to the backend API. "
                "Check the API URL and backend availability."
            )

        except requests.exceptions.HTTPError as error:
            status_code = (
                error.response.status_code
                if error.response is not None
                else "unknown"
            )

            st.error(
                f"Backend HTTP error ({status_code}). "
                "Check the backend logs for details."
            )

            if error.response is not None:
                st.caption(error.response.text[:1000])

        except Exception as error:
            st.error(f"Unexpected error: {error}")


with st.sidebar:
    st.markdown("## 📡 System Status")

    try:
        health = requests.get(
            f"{API_URL}/health",
            timeout=15,
        )

        if health.status_code == 200:
            st.success("API: Online")
        else:
            st.error(f"API: HTTP {health.status_code}")

    except requests.exceptions.RequestException:
        st.error("API: Offline — may be starting up")

    try:
        stats_response = requests.get(
            f"{API_URL}/stats",
            timeout=15,
        )
        stats_response.raise_for_status()
        stats = stats_response.json()

        if "total_vectors" in stats:
            st.metric(
                "Total Chunks",
                stats["total_vectors"],
            )

    except (requests.exceptions.RequestException, ValueError):
        pass

    st.markdown("---")
    st.markdown("## 📖 About")

    st.markdown("""
**MacroEcon Hub** is a live RAG system covering:

- 🇺🇸 US Macro Data (FRED)
- 🌍 Global Data (World Bank, IMF)
- 📰 Live News (Reuters, BBC, CNBC)
- 📚 Reference (Wikipedia)

**Updates every 30 minutes**
""")

    st.markdown("---")
    st.markdown("## 🔍 Topics Covered")

    topics = [
        "Inflation",
        "GDP",
        "Interest Rates",
        "Unemployment",
        "Central Banks",
        "Recession",
        "Business Cycle",
        "Monetary Policy",
    ]

    for topic in topics:
        st.markdown(f"- {topic}")
