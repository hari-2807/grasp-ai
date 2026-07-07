import fitz  # PyMuPDF


def parse(file_bytes: bytes, filename: str = None) -> dict:
    """Extract clean text and metadata from a PDF file."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        return {
            "title": filename or "Uploaded PDF",
            "text": "",
            "word_count": 0,
            "page_count": 0,
            "source_type": "pdf",
            "error": str(e),
        }

    try:
        pages_text = [page.get_text() for page in doc]
        raw_text = " ".join(pages_text)
        cleaned = " ".join(raw_text.split())
        word_count = len(cleaned.split())
        page_count = len(doc)

        meta_title = (doc.metadata.get("title") or "").strip()
        title = meta_title or filename or "Uploaded PDF"

        is_likely_scanned = word_count == 0 and page_count > 0
    finally:
        doc.close()

    return {
        "title": title,
        "text": cleaned,
        "word_count": word_count,
        "page_count": page_count,
        "source_type": "pdf",
        "likely_scanned": is_likely_scanned,
    }
