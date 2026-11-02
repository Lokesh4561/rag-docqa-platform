"""Postgres + pgvector connection and schema."""

import psycopg
from pgvector.psycopg import register_vector

from app.config import DATABASE_URL, EMBED_DIM

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS documents (
    id            SERIAL PRIMARY KEY,
    source        TEXT UNIQUE NOT NULL,
    title         TEXT,
    content_hash  TEXT NOT NULL,
    ingested_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id           SERIAL PRIMARY KEY,
    document_id  INT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index  INT NOT NULL,
    content      TEXT NOT NULL,
    embedding    vector({EMBED_DIM}) NOT NULL,
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw
    ON chunks USING hnsw (embedding vector_cosine_ops);
"""


def get_conn() -> psycopg.Connection:
    """Open a connection with the pgvector type registered."""
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn


def init_db() -> None:
    """Create tables and the vector index if they do not exist yet."""
    with get_conn() as conn:
        conn.execute(SCHEMA)


if __name__ == "__main__":
    init_db()
    print("Database initialised.")
