"""Read complete persisted document text independently of embeddings or retrieval."""

from collections.abc import Mapping

from app.orchestration.runtime import check_active

FETCH_BATCH_SIZE = 100


class DocumentStoreError(RuntimeError):
    pass


def read_stored_chunks(document_id: str, index) -> list[dict]:
    if not document_id:
        raise DocumentStoreError("Choose an uploaded PDF first.")
    prefix, ids = f"{document_id}-chunk-", set()
    check_active()
    for page in index.list(prefix=prefix):
        check_active()
        items = page if isinstance(page, list) else _field(page, "vectors", [])
        for item in items:
            chunk_id = item if isinstance(item, str) else _field(item, "id", "")
            if not isinstance(chunk_id, str) or not chunk_id.startswith(prefix) or not chunk_id[len(prefix):].isdigit():
                raise DocumentStoreError("The document store returned an invalid chunk ID.")
            ids.add(chunk_id)
    ordered = sorted(ids, key=lambda value: int(value[len(prefix):]))
    chunks = []
    for start in range(0, len(ordered), FETCH_BATCH_SIZE):
        check_active()
        batch = ordered[start:start + FETCH_BATCH_SIZE]
        vectors = _field(index.fetch(ids=batch), "vectors", {})
        for chunk_id in batch:
            vector = vectors.get(chunk_id)
            if vector is None:
                raise DocumentStoreError("Some PDF chunks are unavailable. Please try again.")
            metadata = _field(vector, "metadata", {})
            if not isinstance(metadata, Mapping) or metadata.get("document_id") != document_id:
                raise DocumentStoreError("A stored chunk belongs to a different document.")
            chunks.append({"id": chunk_id, "score": 0.0, "metadata": dict(metadata)})
    return chunks


def _field(value, name, default=None):
    return value.get(name, default) if isinstance(value, Mapping) else getattr(value, name, default)
