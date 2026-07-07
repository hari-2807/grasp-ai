import os
import io
from google import genai
from google.genai import types
import PIL.Image


def _client(api_key: str = None) -> genai.Client:
    return genai.Client(api_key=api_key or os.getenv("GEMINI_API_KEY"))


def complete(prompt: str, model: str = "gemini-3-flash", api_key: str = None) -> dict:
    """Send a text prompt to Gemini and return text + token counts."""
    client = _client(api_key)
    resp = client.models.generate_content(model=model, contents=prompt)
    return {
        "text": resp.text,
        "input_tokens": resp.usage_metadata.prompt_token_count,
        "output_tokens": resp.usage_metadata.candidates_token_count,
        "model": model,
    }


def describe_image(image_bytes: bytes, prompt: str, api_key: str = None) -> dict:
    """Send an image + prompt to Gemini Vision and return description + token counts."""
    client = _client(api_key)
    img = PIL.Image.open(io.BytesIO(image_bytes))
    model = "gemini-3-flash"
    resp = client.models.generate_content(model=model, contents=[prompt, img])
    return {
        "text": resp.text,
        "input_tokens": resp.usage_metadata.prompt_token_count,
        "output_tokens": resp.usage_metadata.candidates_token_count,
        "model": model,
    }
