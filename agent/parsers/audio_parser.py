import os
from openai import OpenAI


def transcribe(audio_bytes: bytes, filename: str = "audio.mp3", api_key: str = None) -> dict:
    """Transcribe an audio file using OpenAI Whisper and return the text."""
    client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    resp = client.audio.transcriptions.create(
        model="whisper-1",
        file=(filename, audio_bytes),
        response_format="text",
    )

    text = resp if isinstance(resp, str) else resp.text
    word_count = len(text.split())

    return {
        "title": "Meeting / Recording",
        "text": text,
        "word_count": word_count,
        "estimated_duration_mins": round(word_count / 150, 1),
        "source_type": "audio",
    }
