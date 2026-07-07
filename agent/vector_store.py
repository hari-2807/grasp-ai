import os
from databricks.vector_search.client import VectorSearchClient

CATALOG = "grasp_catalog"
SCHEMA = "grasp_poc"
INDEX_NAME = f"{CATALOG}.{SCHEMA}.embeddings_index"
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.embeddings"
ENDPOINT_NAME = os.getenv("DATABRICKS_VS_ENDPOINT", "grasp-vector-endpoint")


def _client() -> VectorSearchClient:
    return VectorSearchClient(
        workspace_url=os.getenv("DATABRICKS_HOST"),
        personal_access_token=os.getenv("DATABRICKS_TOKEN"),
    )


def get_or_create_index(embedding_dim: int = 1536):
    """Fetch the vector index, creating it if it doesn't exist yet."""
    vsc = _client()
    try:
        return vsc.get_index(endpoint_name=ENDPOINT_NAME, index_name=INDEX_NAME)
    except Exception:
        return vsc.create_delta_sync_index(
            endpoint_name=ENDPOINT_NAME,
            source_table_name=SOURCE_TABLE,
            index_name=INDEX_NAME,
            pipeline_type="TRIGGERED",
            primary_key="chunk_id",
            embedding_dimension=embedding_dim,
            embedding_vector_column="embedding",
        )


def upsert_chunks(session_id: str, embedded_chunks: list[dict]) -> dict:
    """Insert embedded chunks (from embedder.py) into the vector index.

    Each chunk becomes one row: chunk_id, session_id, text, embedding, metadata.
    """
    index = get_or_create_index()

    rows = []
    for chunk in embedded_chunks:
        if chunk.get("embedding") is None:
            continue
        rows.append({
            "chunk_id": f"{session_id}_{chunk['chunk_index']}",
            "session_id": session_id,
            "text": chunk["text"],
            "embedding": chunk["embedding"],
            "start_word": chunk["start_word"],
            "end_word": chunk["end_word"],
        })

    if not rows:
        return {"upserted": 0, "error": "No valid embedded chunks to upsert"}

    try:
        index.upsert(rows)
    except Exception as e:
        return {"upserted": 0, "error": str(e)}

    return {"upserted": len(rows)}


def search(session_id: str, query_embedding: list[float], num_results: int = 5) -> list[dict]:
    """Find the most relevant chunks for a query within a specific session."""
    index = get_or_create_index()

    try:
        results = index.similarity_search(
            query_vector=query_embedding,
            columns=["chunk_id", "session_id", "text", "start_word", "end_word"],
            filters={"session_id": session_id},
            num_results=num_results,
        )
    except Exception as e:
        return [{"text": "", "error": str(e)}]

    data = results.get("result", {}).get("data_array", [])
    columns = [c["name"] for c in results.get("manifest", {}).get("columns", [])]

    return [dict(zip(columns, row)) for row in data]
