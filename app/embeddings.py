"""Embedding generation with a small, free, local model."""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import EMBED_MODEL


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    # Downloaded once (about 90 MB), then cached on disk.
    return SentenceTransformer(EMBED_MODEL)


def embed_texts(texts: list[str]) -> np.ndarray:
    """Return one normalised embedding vector per input text."""
    return get_model().encode(
        texts,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=len(texts) > 64,
    )


def embed_query(query: str) -> np.ndarray:
    return embed_texts([query])[0]
