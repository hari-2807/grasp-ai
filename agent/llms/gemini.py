import os
import io
import google.generativeai as genai
import PIL.Image


def _configure(api_key: str = None):
    genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))


def complete(prompt: str, model: str = "gemini-1.5-flash", api_key: str = None) -> dict:
    """Send a text prompt to Gemini and return text + token counts."""
    _configure(api_key)
    m = genai.GenerativeModel(model)
    resp = m.generate_content(prompt)
    return {
        "text": resp.text,
        "input_tokens": resp.usage_metadata.prompt_token_count,
        "output_tokens": resp.usage_metadata.candidates_token_count,
        "model": model,
    }


def describe_image(image_bytes: bytes, prompt: str, api_key: str = None) -> dict:
    """Send an image + prompt to Gemini Vision and return description + token counts."""
    _configure(api_key)
    img = PIL.Image.open(io.BytesIO(image_bytes))
    m = genai.GenerativeModel("gemini-1.5-flash")
    resp = m.generate_content([prompt, img])
    return {
        "text": resp.text,
        "input_tokens": resp.usage_metadata.prompt_token_count,
        "output_tokens": resp.usage_metadata.candidates_token_count,
        "model": "gemini-1.5-flash",
    }
