def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """Split text into overlapping word-based chunks for embedding and retrieval.

    Each chunk is `chunk_size` words with `overlap` words shared between
    consecutive chunks, so context isn't lost at chunk boundaries.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    words = text.split()
    total_words = len(words)

    if total_words == 0:
        return []

    chunks = []
    start = 0
    chunk_index = 0
    stride = chunk_size - overlap

    while start < total_words:
        end = min(start + chunk_size, total_words)
        chunk_words = words[start:end]

        chunks.append({
            "chunk_index": chunk_index,
            "text": " ".join(chunk_words),
            "word_count": len(chunk_words),
            "start_word": start,
            "end_word": end,
        })

        chunk_index += 1
        start += stride

        if end == total_words:
            break

    return chunks


def needs_chunking(text: str, threshold_words: int = 2000) -> bool:
    """Quick check for whether content is long enough to benefit from chunking."""
    return len(text.split()) > threshold_words
