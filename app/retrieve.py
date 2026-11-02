"""Semantic search over stored chunks using cosine distance."""

import psycopg

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


def _rows_to_dicts(rows) -> list[dict]:
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


def search(query: str, k: int = TOP_K, conn: psycopg.Connection | None = None) -> list[dict]:
    """Return the k chunks most similar to the query.

    Pass an open `conn` to reuse one connection across many searches (much faster);
    otherwise a short-lived connection is opened for this call.
    """
    vec = embed_query(query)
    params = {"vec": vec, "k": k}
    if conn is not None:
        return _rows_to_dicts(conn.execute(SEARCH_SQL, params).fetchall())
    with get_conn() as own_conn:
        return _rows_to_dicts(own_conn.execute(SEARCH_SQL, params).fetchall())
