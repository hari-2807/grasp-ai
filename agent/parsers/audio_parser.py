import os
import tempfile

from agent.llms import openai as openai_llm


def transcribe(audio_bytes: bytes, filename: str = "audio.mp3", api_key: str = None) -> dict:
    """Transcribe an audio file using OpenAI Whisper and return the text."""
    suffix = os.path.splitext(filename)[1] or ".mp3"

    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            result = openai_llm.transcribe(tmp.name, api_key=api_key)
    except Exception as e:
        return {
            "title": "Meeting / Recording",
            "text": "",
            "word_count": 0,
            "estimated_duration_mins": 0,
            "source_type": "audio",
            "error": str(e),
        }

    text = result["text"]
    word_count = len(text.split())

    return {
        "title": "Meeting / Recording",
        "text": text,
        "word_count": word_count,
        "estimated_duration_mins": round(word_count / 150, 1),
        "source_type": "audio",
    }
