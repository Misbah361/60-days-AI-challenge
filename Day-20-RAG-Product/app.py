"""FastAPI server. Run:  uvicorn app:app --port 8000"""
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from knowledge_base import DOCUMENTS
from rag_engine import RAGEngine

app = FastAPI(title="Veridia Knowledge Assistant")
engine = RAGEngine(DOCUMENTS)  # loaded ONCE at startup, not per request


class AskRequest(BaseModel):
    query: str
    category: Optional[str] = None


@app.post("/ask")
def ask_endpoint(req: AskRequest):
    filters = {"category": req.category} if req.category else {}
    return engine.ask(req.query, **filters)
