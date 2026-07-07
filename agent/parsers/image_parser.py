from agent.llms import gemini

_EXTRACT_PROMPT = (
    "Look at this image carefully. "
    "Extract ALL text, data, tables, diagrams, labels, and key information you can see. "
    "Return everything as structured plain text. Be thorough."
)


def parse(image_bytes: bytes, api_key: str = None) -> dict:
    """Use Gemini Vision to extract all content from an image."""
    try:
        result = gemini.describe_image(image_bytes, _EXTRACT_PROMPT, api_key=api_key)
    except Exception as e:
        return {
            "title": "Image",
            "text": "",
            "word_count": 0,
            "source_type": "image",
            "error": str(e),
        }

    text = result["text"]

    return {
        "title": "Image",
        "text": text,
        "word_count": len(text.split()),
        "source_type": "image",
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "model": result["model"],
    }
