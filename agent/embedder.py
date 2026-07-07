import os
from openai import AzureOpenAI

MODEL_ID = "text-embedding-3-small"
BATCH_SIZE = 100


def _client(api_key: str = None, endpoint: str = None) -> AzureOpenAI:
    return AzureOpenAI(
        api_key=api_key or os.getenv("AZURE_OPENAI_KEY"),
        azure_endpoint=endpoint or os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version="2024-10-21",
    )


def embed_chunks(chunks: list[dict], api_key: str = None, endpoint: str = None) -> list[dict]:
    """Embed a list of text chunks (from chunker.py) and attach vectors to each.

    Batches requests to stay within API limits and avoid unnecessary calls.
    """
    if not chunks:
        return []

    client = _client(api_key, endpoint)
    embedded_chunks = []

    for batch_start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[batch_start:batch_start + BATCH_SIZE]
        texts = [c["text"] for c in batch]

        try:
            resp = client.embeddings.create(model=MODEL_ID, input=texts)
        except Exception as e:
            for chunk in batch:
                embedded_chunks.append({
                    **chunk,
                    "embedding": None,
                    "error": str(e),
                })
            continue

        for chunk, item in zip(batch, resp.data):
            embedded_chunks.append({
                **chunk,
                "embedding": item.embedding,
                "model": MODEL_ID,
            })

    return embedded_chunks


def embed_query(query: str, api_key: str = None, endpoint: str = None) -> list[float]:
    """Embed a single query string (e.g. a user's question) for similarity search."""
    client = _client(api_key, endpoint)
    resp = client.embeddings.create(model=MODEL_ID, input=[query])
    return resp.data[0].embedding
