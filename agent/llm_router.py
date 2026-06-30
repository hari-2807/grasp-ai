from dataclasses import dataclass

GBP_PER_USD = 0.79

PRICING = {
    "gemini-1.5-flash": {"input_per_m": 0.075, "output_per_m": 0.30},
    "claude-haiku-4-5-20251001": {"input_per_m": 0.80, "output_per_m": 4.00},
    "claude-sonnet-4-6": {"input_per_m": 3.00, "output_per_m": 15.00},
}

MODEL_LABELS = {
    "gemini-1.5-flash": "Gemini Flash",
    "claude-haiku-4-5-20251001": "Claude Haiku",
    "claude-sonnet-4-6": "Claude Sonnet",
}


@dataclass
class RouterDecision:
    model: str
    label: str
    provider: str
    reason: str


def route(source_type: str, word_count: int, mode: str) -> RouterDecision:
    """Pick the cheapest model that can handle the task."""
    if mode == "analysis":
        return RouterDecision(
            "claude-sonnet-4-6", "Claude Sonnet", "anthropic",
            "Analysis needs deep reasoning"
        )

    if source_type == "image":
        return RouterDecision(
            "gemini-1.5-flash", "Gemini Flash", "gemini",
            "Vision — Gemini Flash multimodal"
        )

    if source_type == "audio":
        return RouterDecision(
            "claude-haiku-4-5-20251001", "Whisper + Claude Haiku", "openai+anthropic",
            "Audio transcribed by Whisper, summarised by Haiku"
        )

    if word_count < 2000:
        return RouterDecision(
            "gemini-1.5-flash", "Gemini Flash", "gemini",
            "Short content — Flash is sufficient and cheapest"
        )
    elif word_count < 8000:
        return RouterDecision(
            "claude-haiku-4-5-20251001", "Claude Haiku", "anthropic",
            "Medium content — Haiku handles well at low cost"
        )
    else:
        return RouterDecision(
            "claude-haiku-4-5-20251001", "Claude Haiku", "anthropic",
            "Long content — Haiku with chunking"
        )


def estimate_cost_gbp(model: str, input_tokens: int, output_tokens: int) -> float:
    p = PRICING.get(model, PRICING["claude-sonnet-4-6"])
    usd = (input_tokens / 1_000_000 * p["input_per_m"]) + \
          (output_tokens / 1_000_000 * p["output_per_m"])
    return round(usd * GBP_PER_USD, 5)
