from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import QDRANT_COLLECTION

app = FastAPI(title="MacroEcon Hub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class QueryRequest(BaseModel):
    query: str

class TimeseriesRequest(BaseModel):
    indicator: str
    country: str = "US"
    start_year: int = None
    end_year: int = None

@app.get("/")
def root():
    return {"status": "MacroEcon Hub is live"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query")
def query_endpoint(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        from api.pipeline import run_pipeline
        return run_pipeline(request.query)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
def stats():
    try:
        from scheduler.storage.qdrant_store import get_client as get_qdrant
        client = get_qdrant()
        info = client.get_collection(QDRANT_COLLECTION)
        return {
            "total_vectors": info.vectors_count,
            "collection": QDRANT_COLLECTION
        }
    except Exception as e:
        return {"error": str(e)}