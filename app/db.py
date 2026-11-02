"""Postgres + pgvector connection and schema."""

import time

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

# Fail fast instead of hanging, and keep idle connections alive (important for serverless Postgres like Neon).
CONNECT_KWARGS = {
    "autocommit": True,
    "connect_timeout": 10,
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 10,
    "keepalives_count": 3,
}
STATEMENT_TIMEOUT_MS = 30_000


def get_conn(retries: int = 3) -> psycopg.Connection:
    """Open a connection with the pgvector type registered.

    Retries with exponential backoff, because serverless databases (e.g. Neon)
    can drop the first connection while waking up from auto-suspend.
    """
    for attempt in range(1, retries + 1):
        try:
            conn = psycopg.connect(DATABASE_URL, **CONNECT_KWARGS)
            conn.execute(f"SET statement_timeout = {STATEMENT_TIMEOUT_MS}")
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            register_vector(conn)
            return conn
        except psycopg.OperationalError:
            if attempt == retries:
                raise
            wait = 2 ** attempt
            print(f"Database connection failed (attempt {attempt}/{retries}), retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError("unreachable")


def init_db() -> None:
    """Create tables and the vector index if they do not exist yet."""
    with get_conn() as conn:
        conn.execute(SCHEMA)


if __name__ == "__main__":
    init_db()
    print("Database initialised.")
