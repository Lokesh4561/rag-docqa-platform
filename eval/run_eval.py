"""Retrieval evaluation: does the right document show up in the top-k results?

Metrics:
  hit@k : share of questions whose expected document appears in the top k results
  MRR   : mean reciprocal rank of the expected document (1.0 = always ranked first)

Run with:  python -m eval.run_eval        (or: python -m eval.run_eval 10   for k=10)
Re-run it after every change (chunk size, overlap, embedding model) and record the scores in the README.
"""

import json
import sys
import time
from pathlib import Path

import psycopg

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, EMBED_MODEL, TOP_K
from app.db import get_conn
from app.retrieve import search

QUESTIONS_FILE = Path(__file__).parent / "questions.jsonl"


def load_questions(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def search_with_retry(question: str, k: int, state: dict) -> list[dict]:
    """Search on a shared connection; if the database drops it, reconnect once and retry."""
    try:
        return search(question, k, conn=state["conn"])
    except psycopg.OperationalError:
        print("  connection lost, reconnecting...")
        try:
            state["conn"].close()
        except Exception:
            pass
        state["conn"] = get_conn()
        return search(question, k, conn=state["conn"])


def main(k: int = TOP_K) -> None:
    questions = load_questions(QUESTIONS_FILE)
    n = len(questions)
    hits, rr_total = 0, 0.0
    started = time.time()
    state = {"conn": get_conn()}

    try:
        for i, q in enumerate(questions, start=1):
            titles = [r["title"] for r in search_with_retry(q["question"], k, state)]
            expected = q["expected_title"]
            if expected in titles:
                hits += 1
                rr_total += 1 / (titles.index(expected) + 1)
            else:
                print(f"MISS: {q['question']}  (expected '{expected}', got {titles[:3]})")
            if i % 10 == 0:
                print(f"  ...{i}/{n} questions done")
    finally:
        state["conn"].close()

    print(f"\nConfig: model={EMBED_MODEL}, chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}, k={k}")
    print(f"Questions: {n}  (in {time.time() - started:.0f}s)")
    print(f"hit@{k}: {hits / n:.2%}")
    print(f"MRR:    {rr_total / n:.3f}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else TOP_K)
