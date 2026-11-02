"""Build a synthetic evaluation set: the LLM writes questions that can be answered from each document.

Run from the project folder:  python -m scripts.generate_questions
Output: eval/questions.jsonl (the previous file is kept as eval/questions_backup.jsonl)

Each line looks like:
  {"question": "...", "expected_title": "<file name without extension>", "generated": true}
"""

import json
import random
import re
import shutil
from pathlib import Path

from app.config import LLM_MODEL, RAW_DATA_DIR
from app.llm import get_client

SUPPORTED = {".txt", ".md"}
QUESTIONS_PER_DOC = 2
MAX_DOCS = 50
PASSAGE_CHARS = 4000
OUT_FILE = Path("eval/questions.jsonl")

PROMPT = """Read the passage below and write {n} specific questions that can be answered using ONLY this passage.
Each question must clearly refer to the passage's subject by name, so it points to this topic and not a general one.
Return ONLY a JSON list of strings, with no other text.

Passage:
{passage}"""


def ask_llm(passage: str, n: int) -> list[str]:
    response = get_client().chat.completions.create(
        model=LLM_MODEL,
        temperature=0.3,
        messages=[{"role": "user", "content": PROMPT.format(n=n, passage=passage)}],
    )
    text = response.choices[0].message.content or ""
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return []
    try:
        questions = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    return [q.strip() for q in questions if isinstance(q, str) and len(q.strip()) > 10][:n]


def main() -> None:
    files = sorted(p for p in Path(RAW_DATA_DIR).rglob("*") if p.suffix.lower() in SUPPORTED)
    random.Random(42).shuffle(files)  # fixed seed -> same sample every run
    files = files[:MAX_DOCS]

    rows = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        try:
            questions = ask_llm(text[:PASSAGE_CHARS], QUESTIONS_PER_DOC)
        except Exception as exc:
            print(f"failed  {path.name}: {exc}")
            continue
        rows += [{"question": q, "expected_title": path.stem, "generated": True} for q in questions]
        print(f"{len(questions)} questions  {path.name}")

    if not rows:
        print("No questions were generated. Check your LLM settings in .env")
        return

    if OUT_FILE.exists():
        shutil.copy(OUT_FILE, OUT_FILE.with_name("questions_backup.jsonl"))
    OUT_FILE.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    print(f"\nSaved {len(rows)} questions to {OUT_FILE}")


if __name__ == "__main__":
    main()
