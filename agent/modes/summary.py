from agent.llms import claude, gemini
from agent.llm_router import route, estimate_cost_gbp

_SYSTEM = """You are a smart assistant that makes complex things easy to understand.
Read the content and give a SHORT, CLEAR summary in plain English.

Format your response exactly like this:

**TL;DR**
2-3 sentences. What is this about and why does it matter.

**Key Points**
• Point 1
• Point 2
• Point 3
• Point 4 (max 5 points)

Rules:
- Write like you're explaining to a smart friend, not an expert
- No jargon unless you explain it immediately
- Total response must be under 200 words
- Be direct — no filler phrases like "This document discusses..." """


def run(content: dict, anthropic_key: str = None, gemini_key: str = None) -> dict:
    """Summarise any content using the cheapest suitable model."""
    text = content["text"]
    word_count = content.get("word_count", len(text.split()))
    source_type = content.get("source_type", "web")

    decision = route(source_type, word_count, "summary")

    # truncate very long content — Haiku context is generous but keep cost low
    trimmed = text[:15000]
    user_msg = f"Summarise this in short, plain English:\n\n{trimmed}"

    if decision.provider == "gemini":
        prompt = f"{_SYSTEM}\n\nUser: {user_msg}"
        result = gemini.complete(prompt, api_key=gemini_key)
    else:
        result = claude.complete(
            system=_SYSTEM,
            user=user_msg,
            model=decision.model,
            max_tokens=500,
            api_key=anthropic_key,
        )

    cost = estimate_cost_gbp(decision.model, result["input_tokens"], result["output_tokens"])

    return {
        "output": result["text"],
        "model": decision.label,
        "model_id": decision.model,
        "reason": decision.reason,
        "cost_gbp": cost,
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
    }
