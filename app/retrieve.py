"""Semantic search over stored chunks using cosine distance."""

from app.config import TOP_K
from app.db import get_conn
from app.embeddings import embed_query

SEARCH_SQL = """
SELECT c.content,
       d.title,
       d.source,
       c.chunk_index,
       1 - (c.embedding <=> %(vec)s) AS score
FROM chunks c
JOIN documents d ON d.id = c.document_id
ORDER BY c.embedding <=> %(vec)s
LIMIT %(k)s
"""


def search(query: str, k: int = TOP_K) -> list[dict]:
    vec = embed_query(query)
    with get_conn() as conn:
        rows = conn.execute(SEARCH_SQL, {"vec": vec, "k": k}).fetchall()
    return [
        {
            "content": r[0],
            "title": r[1],
            "source": r[2],
            "chunk_index": r[3],
            "score": round(float(r[4]), 4),
        }
        for r in rows
    ]
