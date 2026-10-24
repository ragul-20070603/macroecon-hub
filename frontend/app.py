
import os
import json
import requests
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv(
    "API_URL",
    "https://macroecon-hub-api.onrender.com",
).rstrip("/")

REQUEST_TIMEOUT = 120

st.set_page_config(
    page_title="MacroEcon Hub",
    page_icon="📊",
    layout="wide",
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "macro_query" not in st.session_state:
    st.session_state["macro_query"] = ""

if "submit_macro_query" not in st.session_state:
    st.session_state["submit_macro_query"] = False


def select_example(example):
    """Runs before the next script execution and widget creation."""
    st.session_state["macro_query"] = example
    st.session_state["submit_macro_query"] = True


# --------------------------------------------------
# RESPONSE PARSING
# --------------------------------------------------

def normalize_response(data):
    """Safely unwrap common JSON response structures."""

    for _ in range(6):
        if isinstance(data, str):
            try:
                data = json.loads(data)
                continue
            except (json.JSONDecodeError, TypeError):
                return {"answer": data}

        if not isinstance(data, dict):
            return {"answer": str(data)}

        if "answer" in data:
            return data

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

    if isinstance(data, dict):
        return data

    return {"answer": str(data)}


def display_sources(sources):
    if not sources:
        return

    if isinstance(sources, str):
        sources = [sources]

    if isinstance(sources, list):
        valid_sources = [
            str(source)
            for source in sources
            if source
        ]

        if valid_sources:
            with st.expander("📚 Sources used"):
                for source in valid_sources:
                    st.markdown(f"- {source}")


# --------------------------------------------------
# API REQUEST
# --------------------------------------------------

def ask_backend(user_query):
    """Call the backend and render its response safely."""

    try:
        with st.spinner(
            "Searching knowledge base and generating answer..."
        ):
            response = requests.post(
                f"{API_URL}/query",
                json={"query": user_query},
                timeout=REQUEST_TIMEOUT,
            )

        if not response.ok:
            st.error(
                f"Backend returned HTTP {response.status_code}."
            )

            try:
                details = response.json()
                message = (
                    details.get("detail", details)
                    if isinstance(details, dict)
                    else details
                )
                st.caption(f"Details: {str(message)[:1500]}")
            except (ValueError, TypeError):
                st.caption(response.text[:1500])

            return

        try:
            raw_result = response.json()
        except ValueError:
            st.error("The backend did not return valid JSON.")
            st.caption(response.text[:1500])
            return

        result = normalize_response(raw_result)

        if not isinstance(result, dict):
            st.error("The backend response has an unexpected format.")
            return

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
            st.warning(
                "The backend responded, but no answer was returned."
            )

            with st.expander("Inspect API response"):
                st.json(result)

        # -------------------------------
        # TREND CHART
        # -------------------------------

        trend_data = result.get("trend_data")

        if isinstance(trend_data, dict):
            dates = trend_data.get("dates")
            values = trend_data.get("values")

            valid_data = (
                isinstance(dates, list)
                and isinstance(values, list)
                and len(dates) > 0
                and len(dates) == len(values)
            )

            if valid_data:
                try:
                    points = [
                        (date, float(value))
                        for date, value in zip(dates, values)
                        if date is not None
                        and value is not None
                    ]

                    if points:
                        chart_dates, chart_values = zip(*points)

                        st.markdown("### 📈 Trend Chart")

                        fig = go.Figure()

                        fig.add_trace(
                            go.Scatter(
                                x=list(chart_dates),
                                y=list(chart_values),
                                mode="lines",
                                name=str(
                                    result.get("indicator", "Value")
                                ),
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

                except (ValueError, TypeError, KeyError):
                    st.info(
                        "Trend data was returned but could not "
                        "be plotted. The text answer is still available."
                    )

        display_sources(result.get("sources"))

    except requests.exceptions.Timeout:
        st.error(
            "The request timed out. The backend may be starting up "
            "or taking too long. Please try again."
        )

    except requests.exceptions.ConnectionError:
        st.error(
            "Cannot connect to the backend. Check API_URL, "
            "backend availability, and deployment status."
        )

    except requests.exceptions.RequestException as error:
        st.error(f"Network request failed: {error}")

    except Exception as error:
        st.error(f"An unexpected error occurred: {error}")


# --------------------------------------------------
# MAIN UI
# --------------------------------------------------

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
        key="ask_button",
    )

st.markdown("**Example queries:**")

example_queries = [
    "What causes inflation?",
    "US inflation rate trend from 1990 to 2024",
    "What did the Federal Reserve do this week?",
    "Compare GDP growth US vs China",
]

example_columns = st.columns(4)

for index, example in enumerate(example_queries):
    with example_columns[index]:
        st.button(
            example,
            use_container_width=True,
            key=f"example_query_{index}",
            on_click=select_example,
            args=(example,),
        )

st.divider()

# The callback updates session state before this script reruns.
# No widget key is modified after st.text_input is instantiated.
should_submit = st.session_state.pop(
    "submit_macro_query",
    False,
)

if ask_btn or should_submit:
    user_query = st.session_state.get("macro_query", "").strip()

    if user_query:
        ask_backend(user_query)
    else:
        st.warning("Please enter a question or select an example.")


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 📡 System Status")

    try:
        health_response = requests.get(
            f"{API_URL}/health",
            timeout=15,
        )

        if health_response.ok:
            st.success("API: Online")
        else:
            st.error(f"API: HTTP {health_response.status_code}")

    except requests.exceptions.RequestException:
        st.error("API: Offline — may be starting up")

    try:
        stats_response = requests.get(
            f"{API_URL}/stats",
            timeout=15,
        )

        if stats_response.ok:
            stats = stats_response.json()

            if isinstance(stats, dict):
                if "total_vectors" in stats:
                    st.metric(
                        "Total Chunks",
                        stats["total_vectors"],
                    )

    except (
        requests.exceptions.RequestException,
        ValueError,
        TypeError,
    ):
        st.caption("Statistics temporarily unavailable.")

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
