import os
from openai import OpenAI


def _client(api_key: str = None) -> OpenAI:
    return OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))


def complete(
    system: str,
    user: str,
    model: str = "gpt-5.3-instant",
    max_tokens: int = 1024,
    api_key: str = None,
) -> dict:
    """Send a prompt to GPT and return text + token counts."""
    resp = _client(api_key).chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return {
        "text": resp.choices[0].message.content,
        "input_tokens": resp.usage.prompt_tokens,
        "output_tokens": resp.usage.completion_tokens,
        "model": model,
    }


def chat(
    system: str,
    messages: list,
    model: str = "gpt-5.3-instant",
    max_tokens: int = 1024,
    api_key: str = None,
) -> dict:
    """Send a multi-turn conversation to GPT and return text + token counts."""
    full_messages = [{"role": "system", "content": system}] + messages
    resp = _client(api_key).chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=full_messages,
    )
    return {
        "text": resp.choices[0].message.content,
        "input_tokens": resp.usage.prompt_tokens,
        "output_tokens": resp.usage.completion_tokens,
        "model": model,
    }


def transcribe(
    audio_file_path: str,
    model: str = "whisper-1",
    api_key: str = None,
) -> dict:
    """Transcribe an audio file and return the text."""
    client = _client(api_key)
    with open(audio_file_path, "rb") as f:
        resp = client.audio.transcriptions.create(model=model, file=f)
    return {
        "text": resp.text,
        "model": model,
    }
