import os
from azure.storage.blob import BlobServiceClient, ContentSettings

CONTAINER_NAME = "grasp-docs"


def _client() -> BlobServiceClient:
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    return BlobServiceClient.from_connection_string(conn_str)


def _container():
    client = _client()
    container = client.get_container_client(CONTAINER_NAME)
    if not container.exists():
        container.create_container()
    return container


def upload_document(session_id: str, filename: str, file_bytes: bytes, content_type: str = None) -> dict:
    """Upload a document to Azure Blob Storage under the session's folder path."""
    blob_path = f"{session_id}/{filename}"

    try:
        container = _container()
        blob_client = container.get_blob_client(blob_path)
        blob_client.upload_blob(
            file_bytes,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type) if content_type else None,
        )
    except Exception as e:
        return {"success": False, "error": str(e)}

    return {
        "success": True,
        "blob_path": blob_path,
        "url": blob_client.url,
        "size_bytes": len(file_bytes),
    }


def download_document(blob_path: str) -> bytes:
    """Download a document's raw bytes from Blob Storage."""
    container = _container()
    blob_client = container.get_blob_client(blob_path)
    return blob_client.download_blob().readall()


def delete_document(blob_path: str) -> bool:
    """Delete a document from Blob Storage. Returns True if deleted, False if not found."""
    container = _container()
    blob_client = container.get_blob_client(blob_path)
    try:
        blob_client.delete_blob()
        return True
    except Exception:
        return False


def document_exists(blob_path: str) -> bool:
    """Check if a document exists at the given blob path."""
    container = _container()
    blob_client = container.get_blob_client(blob_path)
    return blob_client.exists()
