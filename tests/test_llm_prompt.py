import pytest

pytest.importorskip("openai")

from app.llm import build_prompt  # noqa: E402


def test_prompt_numbers_sources_and_includes_question():
    contexts = [
        {"title": "doc_a", "content": "Alpha text."},
        {"title": "doc_b", "content": "Beta text."},
    ]
    prompt = build_prompt("What is alpha?", contexts)
    assert "[1] (source: doc_a)" in prompt
    assert "[2] (source: doc_b)" in prompt
    assert prompt.strip().endswith("Question: What is alpha?")
