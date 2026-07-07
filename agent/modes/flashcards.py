import json
import re

from agent.llms import gemini
from agent.llm_router import estimate_cost_gbp

MODEL_ID = "gemini-3-flash"
MAX_CHARS = 100000

_SYSTEM = """You create revision flashcards from content so someone can test themselves later.

Return ONLY a JSON array, no other text, no markdown code fences.
Each item must look like: {"question": "...", "answer": "..."}

Generate 6-10 cards covering the most important, testable points.
Questions should be short and specific. Answers should be short — one sentence or a few words."""


def _extract_cards(text: str) -> list:
    match = re.search(r"\[.*\]", text, re.DOTALL)
    raw = match.group(0) if match else text
    return json.loads(raw)


def run(content: dict, gemini_key: str = None) -> dict:
    """Generate revision flashcards from content using Gemini Flash."""
    full_text = content["text"]
    text = full_text[:MAX_CHARS]
    was_truncated = len(full_text) > MAX_CHARS

    prompt = f"{_SYSTEM}\n\nContent:\n\n{text}"

    try:
        result = gemini.complete(prompt, model=MODEL_ID, api_key=gemini_key)
    except Exception as e:
        return {
            "cards": [],
            "error": str(e),
            "model": "Gemini Flash",
            "model_id": MODEL_ID,
            "cost_gbp": 0,
            "truncated": was_truncated,
        }

    try:
        cards = _extract_cards(result["text"])
    except (json.JSONDecodeError, AttributeError):
        cards = []
        parse_error = "Could not generate flashcards from this content — try again."
    else:
        parse_error = None

    cost = estimate_cost_gbp(_MODEL_ID, result["input_tokens"], result["output_tokens"])

    return {
        "cards": cards,
        "errors": parse_error
        "model": "Gemini Flash",
        "model_id": MODEL_ID,
        "cost_gbp": cost,
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "truncated": was_truncated,
    }
