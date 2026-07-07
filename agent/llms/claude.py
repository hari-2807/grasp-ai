import os
import anthropic


def _client(api_key: str = None) -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))


def complete(
    system: str,
    user: str,
    model: str = "claude-haiku-4-5",
    max_tokens: int = 1024,
    api_key: str = None,
) -> dict:
    """Send a prompt to Claude and return text + token counts."""
    resp = _client(api_key).messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return {
        "text": resp.content[0].text,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
        "model": model,
    }


def chat(
    system: str,
    messages: list,
    model: str = "claude-haiku-4-5",
    max_tokens: int = 1024,
    api_key: str = None,
) -> dict:
    """Send a multi-turn conversation to Claude and return text + token counts."""
    resp = _client(api_key).messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    return {
        "text": resp.content[0].text,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
        "model": model,
    }
