import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from scheduler.fetchers.news import fetch_all_news
from scheduler.fetchers.fred import fetch_all_series
from scheduler.fetchers.worldbank import fetch_all_world_bank
from scheduler.fetchers.imf import fetch_all_imf
from scheduler.processing.chunker import prepare_chunks
from scheduler.processing.embedder import embed_chunks
from scheduler.processing.deduplicator import url_dedup
from scheduler.storage.qdrant_store import ensure_collection, upsert_chunks, get_all_hashes
from scheduler.storage.supabase_store import store_timeseries, get_all_url_hashes, store_url_hash
from scheduler.storage.tiering import migrate_tiers

def run_news_ingestion():
    print("\n[SCHEDULER] Starting news ingestion...")
    try:
        existing_hashes = get_all_url_hashes()
        articles = fetch_all_news()
        new_articles = url_dedup(articles, existing_hashes)
        print(f"New articles after dedup: {len(new_articles)}")

        all_chunks = []
        for article in new_articles:
            chunks = prepare_chunks(article)
            all_chunks.extend(chunks)

        if all_chunks:
            embeddings = embed_chunks(all_chunks)
            upsert_chunks(all_chunks, embeddings)
            for article in new_articles:
                store_url_hash(article["url_hash"])

        print(f"[SCHEDULER] News ingestion complete. Stored {len(all_chunks)} chunks.")
    except Exception as e:
        print(f"[SCHEDULER] News ingestion failed: {e}")

def run_timeseries_update():
    print("\n[SCHEDULER] Starting timeseries update...")
    try:
        fred_data = fetch_all_series()
        for name, records in fred_data.items():
            store_timeseries(name, "FRED", records)

        wb_data = fetch_all_world_bank()
        for name, records in wb_data.items():
            store_timeseries(name, "WorldBank", records)

        imf_data = fetch_all_imf()
        for name, records in imf_data.items():
            store_timeseries(name, "IMF", records)

        print("[SCHEDULER] Timeseries update complete.")
    except Exception as e:
        print(f"[SCHEDULER] Timeseries update failed: {e}")

def run_tier_migration():
    print("\n[SCHEDULER] Running tier migration...")
    try:
        migrate_tiers()
        print("[SCHEDULER] Tier migration complete.")
    except Exception as e:
        print(f"[SCHEDULER] Tier migration failed: {e}")

def initialize():
    print("[SCHEDULER] Initializing...")
    ensure_collection()
    run_timeseries_update()
    run_news_ingestion()
    print("[SCHEDULER] Initialization complete.")

if __name__ == "__main__":
    initialize()

    scheduler = BlockingScheduler()

    scheduler.add_job(
        run_news_ingestion,
        trigger=IntervalTrigger(minutes=30),
        id="news_ingestion",
        name="Fetch and ingest live news every 30 minutes"
    )

    scheduler.add_job(
        run_timeseries_update,
        trigger=IntervalTrigger(hours=24),
        id="timeseries_update",
        name="Update FRED, World Bank, IMF data daily"
    )

    scheduler.add_job(
        run_tier_migration,
        trigger=CronTrigger(hour=2, minute=0),
        id="tier_migration",
        name="Migrate stale and archived chunks daily at 2am"
    )

    print("[SCHEDULER] Scheduler started. Running every 30 minutes.")
    scheduler.start()
