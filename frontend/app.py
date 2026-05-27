import streamlit as st
import requests
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="MacroEcon Hub",
    page_icon="📊",
    layout="wide"
)

st.title("📊 MacroEcon Hub")
st.markdown("*A live macroeconomic intelligence system — updated every 30 minutes from global sources*")
st.divider()

col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input(
        "Ask anything about macroeconomics:",
        placeholder="e.g. What was US inflation from 1990 to 2024? / What did the Fed announce this week?"
    )

with col2:
    st.markdown("###")
    ask_btn = st.button("Ask", use_container_width=True, type="primary")

st.markdown("**Example queries:**")
examples = st.columns(4)
example_queries = [
    "What causes inflation?",
    "US inflation rate trend from 1990 to 2024",
    "What did the Federal Reserve do this week?",
    "Compare GDP growth US vs China"
]
for i, ex in enumerate(example_queries):
    with examples[i]:
        if st.button(ex, use_container_width=True):
            query = ex
            ask_btn = True

st.divider()

if ask_btn and query.strip():
    with st.spinner("Searching knowledge base and generating answer..."):
        try:
            response = requests.post(f"{API_URL}/query", json={"query": query}, timeout=30)
            result = response.json()

            if result.get("from_cache"):
                st.caption("⚡ Cached response")

            st.markdown(f"**Query type detected:** `{result.get('query_type', 'conceptual')}`")
            st.markdown("### Answer")
            st.markdown(result["answer"])

            if result.get("trend_data"):
                td = result["trend_data"]
                if td.get("dates") and td.get("values"):
                    st.markdown("### 📈 Trend Chart")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=td["dates"],
                        y=td["values"],
                        mode="lines",
                        name=result.get("indicator", "Value"),
                        line=dict(color="#1f77b4", width=2)
                    ))
                    fig.update_layout(
                        title=f"{result.get('indicator', 'Indicator')} — {result.get('country', 'US')}",
                        xaxis_title="Date",
                        yaxis_title="Value",
                        hovermode="x unified",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

            if result.get("sources"):
                with st.expander("📚 Sources used"):
                    for s in result["sources"]:
                        if s:
                            st.markdown(f"- {s}")

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend API. Make sure the API server is running.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

with st.sidebar:
    st.markdown("## 📡 System Status")
    try:
        health = requests.get(f"{API_URL}/health", timeout=5)
        if health.status_code == 200:
            st.success("API: Online")
        else:
            st.error("API: Offline")
    except Exception:
        st.error("API: Offline")

    try:
        stats = requests.get(f"{API_URL}/stats", timeout=5)
        data = stats.json()
        if "total_vectors" in data:
            st.metric("Total Chunks", data["total_vectors"])
    except Exception:
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
    topics = ["Inflation", "GDP", "Interest Rates", "Unemployment",
              "Central Banks", "Recession", "Business Cycle", "Monetary Policy"]
    for t in topics:
        st.markdown(f"- {t}")
