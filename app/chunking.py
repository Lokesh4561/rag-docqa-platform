"""Text cleaning and chunking. Pure Python with no external dependencies, so it is easy to unit test."""

import re


def clean_text(text: str) -> str:
    """Collapse all whitespace (newlines, tabs, repeated spaces) into single spaces."""
    return re.sub(r"\s+", " ", text or "").strip()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """Split text into overlapping chunks of roughly `chunk_size` characters.

    Chunks end on a word boundary where possible, and each chunk repeats about
    `overlap` characters from the previous one so that context is not lost
    at the edges.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    text = clean_text(text)
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            # Prefer to cut at the last space inside the window.
            space = text.rfind(" ", start, end)
            if space > start:
                end = space

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break

        # Step back by `overlap`, then move forward to the next word start.
        next_start = max(end - overlap, start + 1)
        if text[next_start - 1] != " ":
            nxt = text.find(" ", next_start)
            if nxt != -1 and nxt < end:
                next_start = nxt + 1
        start = next_start

    return chunks
