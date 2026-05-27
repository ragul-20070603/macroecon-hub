# 📊 MacroEcon Hub

A live, self-updating macroeconomic intelligence system that answers any economics question using real-time news, historical data, and comprehensive reference knowledge.

---

## Architecture

```
User → Streamlit Frontend → FastAPI Backend → Qdrant + Supabase + Groq
                                ↑
                    APScheduler Worker (every 30 min)
                    FRED + WorldBank + IMF + NewsAPI + RSS
```

---

## Features

- **Live news ingestion** every 30 minutes from Reuters, BBC, CNBC, FT
- **Historical data** from 1947 to present via FRED, World Bank, IMF
- **Smart query routing** — conceptual, timeseries, news, historical
- **Trend charts** with Plotly for data questions
- **Tiered storage** — hot/warm/cold for efficiency
- **Redis caching** for fast repeated queries
- **Recency-weighted retrieval** — newer data ranked higher

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/yourusername/macroecon-hub
cd macroecon-hub
pip install -r api/requirements.txt
pip install -r scheduler/requirements.txt
pip install -r frontend/requirements.txt
```

### 2. Add API keys

Open `.env` and fill in all values:

```
GROQ_API_KEY=
FRED_API_KEY=
NEWS_API_KEY=
BLS_API_KEY=
ALPHA_VANTAGE_API_KEY=
QDRANT_URL=
QDRANT_API_KEY=
SUPABASE_URL=
SUPABASE_KEY=
UPSTASH_REDIS_URL=
UPSTASH_REDIS_TOKEN=
```

### 3. Set up Supabase tables

Run `supabase_schema.sql` in your Supabase SQL editor.

### 4. Run locally

Terminal 1 — API server:
```bash
uvicorn main:app --reload
```

Terminal 2 — Scheduler:
```bash
python scheduler/main.py
```

Terminal 3 — Frontend:
```bash
cd frontend
streamlit run app.py
```

---

## Deployment

### Render.com (Backend + Scheduler)
1. Push to GitHub
2. Go to render.com → New → Blueprint
3. Connect repo → render.yaml auto-configures both services
4. Add all environment variables in Render dashboard

### Streamlit Cloud (Frontend)
1. Go to share.streamlit.io
2. Connect GitHub repo
3. Set main file: `frontend/app.py`
4. Add `API_URL` secret pointing to your Render API URL

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/query` | POST | Ask a question |
| `/timeseries` | POST | Get raw timeseries data |
| `/stats` | GET | Database statistics |

---

## Sample Queries

- What causes inflation?
- What was US inflation rate from 1990 to 2024?
- What did the Federal Reserve announce this week?
- Compare GDP growth between US and China
- What happened during the 2008 financial crisis?
- What is the current unemployment rate?
- Show me interest rate trends since 1980

---

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| Vector DB | Qdrant Cloud |
| Relational DB | Supabase (PostgreSQL) |
| Cache | Upstash Redis |
| LLM | Groq (Llama 3.3 70B) |
| Embeddings | sentence-transformers |
| Scheduler | APScheduler |
| Deployment | Render.com + Streamlit Cloud |
