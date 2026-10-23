import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FRED_API_KEY = os.getenv("FRED_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BLS_API_KEY = os.getenv("BLS_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_URL")
UPSTASH_REDIS_TOKEN = os.getenv("UPSTASH_REDIS_TOKEN")

QDRANT_COLLECTION = "macroecon_hub"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

HOT_TIER_DAYS = 30
WARM_TIER_DAYS = 90

GROQ_MODEL = "openai/gpt-oss-120b"
TOP_K = 5
SIMILARITY_THRESHOLD = 0.92
CACHE_TTL_SECONDS = 1800

FRED_SERIES = {
    "inflation": "CPIAUCSL",
    "gdp": "GDP",
    "interest_rate": "FEDFUNDS",
    "unemployment": "UNRATE",
    "ppi": "PPIACO",
    "real_gdp_growth": "A191RL1Q225SBEA",
    "10y_treasury": "GS10",
    "money_supply": "M2SL"
}

RSS_FEEDS = [
    "http://feeds.reuters.com/reuters/businessNews",
    "http://feeds.bbci.co.uk/news/business/rss.xml",
    "https://www.cnbc.com/id/20910258/device/rss/rss.html",
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"
]

NEWS_KEYWORDS = [
    "inflation", "interest rate", "GDP", "Federal Reserve",
    "central bank", "recession", "economic growth", "unemployment",
    "monetary policy", "fiscal policy", "CPI", "ECB", "IMF", "World Bank"
]
