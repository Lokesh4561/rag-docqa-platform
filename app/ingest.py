"""Ingestion pipeline: read files -> clean -> chunk -> embed -> store in pgvector.

Idempotent: a file whose content has not changed is skipped, and a changed
file has its old chunks replaced inside one transaction.

Run with:  python -m app.ingest
"""

import hashlib
import time
from pathlib import Path

from pypdf import PdfReader

from app.chunking import chunk_text
from app.config import CHUNK_OVERLAP, CHUNK_SIZE, RAW_DATA_DIR
from app.db import get_conn, init_db
from app.embeddings import embed_texts

SUPPORTED = {".pdf", ".txt", ".md"}


def read_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def ingest_file(conn, path: Path) -> tuple[str, int]:
    text = read_file(path)
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

    row = conn.execute(
        "SELECT id, content_hash FROM documents WHERE source = %s", (str(path),)
    ).fetchone()
    if row and row[1] == content_hash:
        return "skipped (unchanged)", 0

    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    if not chunks:
        return "skipped (no text)", 0
    vectors = embed_texts(chunks)

    with conn.transaction():
        if row:
            doc_id = row[0]
            conn.execute("DELETE FROM chunks WHERE document_id = %s", (doc_id,))
            conn.execute(
                "UPDATE documents SET content_hash = %s, ingested_at = now() WHERE id = %s",
                (content_hash, doc_id),
            )
        else:
            doc_id = conn.execute(
                "INSERT INTO documents (source, title, content_hash) VALUES (%s, %s, %s) RETURNING id",
                (str(path), path.stem, content_hash),
            ).fetchone()[0]

        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO chunks (document_id, chunk_index, content, embedding) VALUES (%s, %s, %s, %s)",
                [(doc_id, i, c, v) for i, (c, v) in enumerate(zip(chunks, vectors))],
            )
    return "ingested", len(chunks)


def main() -> None:
    init_db()
    files = sorted(p for p in Path(RAW_DATA_DIR).rglob("*") if p.suffix.lower() in SUPPORTED)
    if not files:
        print(f"No files found in {RAW_DATA_DIR}. Add .pdf, .txt or .md files and run again.")
        return

    started = time.time()
    total_chunks = 0
    with get_conn() as conn:
        for path in files:
            status, n = ingest_file(conn, path)
            total_chunks += n
            print(f"{status:<20} {n:>5} chunks  {path}")
    print(f"\nDone: {len(files)} files, {total_chunks} new chunks in {time.time() - started:.1f}s")


if __name__ == "__main__":
    main()
