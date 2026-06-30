import fitz  # PyMuPDF


def parse(file_bytes: bytes) -> dict:
    """Extract clean text and metadata from a PDF file."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    pages_text = [page.get_text() for page in doc]
    raw_text = " ".join(pages_text)
    cleaned = " ".join(raw_text.split())
    word_count = len(cleaned.split())

    title = doc.metadata.get("title", "").strip() or "Uploaded PDF"

    return {
        "title": title,
        "text": cleaned,
        "word_count": word_count,
        "page_count": len(doc),
        "source_type": "pdf",
    }
