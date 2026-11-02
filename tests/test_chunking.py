import pytest

from app.chunking import chunk_text, clean_text


def test_clean_text_collapses_whitespace():
    assert clean_text("  hello \n\n world\t ") == "hello world"


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   \n ") == []


def test_short_text_is_single_chunk():
    assert chunk_text("a short sentence", chunk_size=100, overlap=10) == ["a short sentence"]


def test_chunks_respect_size_limit():
    text = " ".join(f"word{i}" for i in range(500))
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)


def test_chunks_do_not_split_words():
    text = " ".join(f"word{i}" for i in range(200))
    words = set(text.split())
    for chunk in chunk_text(text, chunk_size=60, overlap=15):
        assert set(chunk.split()) <= words


def test_all_text_is_covered():
    text = " ".join(f"w{i}" for i in range(300))
    chunks = chunk_text(text, chunk_size=80, overlap=20)
    covered = set(" ".join(chunks).split())
    assert covered == set(text.split())


def test_chunks_overlap():
    text = " ".join(f"w{i}" for i in range(300))
    chunks = chunk_text(text, chunk_size=80, overlap=20)
    for prev, nxt in zip(chunks, chunks[1:]):
        assert set(prev.split()) & set(nxt.split()), "consecutive chunks should share words"


@pytest.mark.parametrize("size,overlap", [(0, 0), (100, 100), (100, -1)])
def test_invalid_arguments_raise(size, overlap):
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=size, overlap=overlap)
