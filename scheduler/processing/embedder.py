import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from config import EMBEDDING_MODEL

_model = None

def get_model():
    global _model
    if _model is None:
        from fastembed import TextEmbedding
        name = EMBEDDING_MODEL
        if "/" not in name:
            name = "sentence-transformers/" + name
        _model = TextEmbedding(model_name=name)
    return _model

def embed_chunks(chunks):
    model = get_model()
    texts = [c["text"] for c in chunks]
    return [e.tolist() for e in model.embed(texts)]

def embed_query(query):
    model = get_model()
    return list(model.embed([query]))[0].tolist()