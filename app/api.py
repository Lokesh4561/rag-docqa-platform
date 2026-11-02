"""REST API.

Run locally with:  uvicorn app.api:app --reload
Interactive docs:  http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import TOP_K
from app.db import init_db
from app.llm import generate_answer
from app.retrieve import search


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="DocQA - RAG Platform", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Query(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    top_k: int = Field(default=TOP_K, ge=1, le=20)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/search")
def search_endpoint(q: Query) -> dict:
    return {"results": search(q.question, q.top_k)}


@app.post("/ask")
def ask_endpoint(q: Query) -> dict:
    contexts = search(q.question, q.top_k)
    if not contexts:
        raise HTTPException(status_code=404, detail="No documents ingested yet. Run: python -m app.ingest")
    try:
        answer = generate_answer(q.question, contexts)
    except Exception as exc:  # LLM endpoint down, bad key, etc.
        raise HTTPException(status_code=502, detail=f"LLM call failed: {exc}") from exc
    return {
        "answer": answer,
        "sources": [
            {"n": i, "title": c["title"], "source": c["source"], "score": c["score"]}
            for i, c in enumerate(contexts, start=1)
        ],
    }
