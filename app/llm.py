"""Answer generation with any OpenAI-compatible LLM endpoint."""

from functools import lru_cache

from openai import OpenAI

from app.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using ONLY the provided context. "
    "Cite the sources you used with their numbers, like [1] or [2]. "
    "If the context does not contain the answer, say you don't know."
)


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    return OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)


def build_prompt(question: str, contexts: list[dict]) -> str:
    blocks = [f"[{i}] (source: {c['title']})\n{c['content']}" for i, c in enumerate(contexts, start=1)]
    return "Context:\n" + "\n\n".join(blocks) + f"\n\nQuestion: {question}"


def generate_answer(question: str, contexts: list[dict]) -> str:
    response = get_client().chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(question, contexts)},
        ],
    )
    return response.choices[0].message.content
