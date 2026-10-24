from typing import Any

from app.services.chunk_ids import chunk_index_of, document_id_of, make_chunk_id
from app.services.pinecone_index import get_index

_current_chunks: list[dict[str, Any]] = []


def add_chunks(chunks: list[dict[str, Any]]) -> None:
    _current_chunks.extend(chunks)


def remove_chunks(document_id: str) -> None:
    _current_chunks[:] = [
        chunk for chunk in _current_chunks
        if document_id_of(chunk) != document_id
    ]


def get_current_chunks(document_id: str | None = None):
    if document_id is None:
        return list(_current_chunks)
    return [
        chunk for chunk in _current_chunks
        if document_id_of(chunk) == document_id
    ]


def get_chunks_by_indexes(indexes, document_id: str | None = None):
    if not indexes:
        return []

    current_by_index = {
        (document_id_of(chunk), chunk_index_of(chunk)): chunk
        for chunk in _current_chunks
    }
    found = [
        current_by_index[(document_id, index)]
        for index in indexes
        if (document_id, index) in current_by_index
    ]
    missing_indexes = [
        index for index in indexes
        if (document_id, index) not in current_by_index
    ]

    if missing_indexes:
        found.extend(_fetch_from_pinecone(document_id, missing_indexes))
        found.sort(key=lambda chunk: chunk_index_of(chunk) or 0)

    return found


def _fetch_from_pinecone(document_id: str | None, indexes) -> list[dict[str, Any]]:
    ids = [make_chunk_id(document_id, index) for index in indexes]
    response = get_index().fetch(ids=ids)
    vectors = (
        response.get("vectors", {})
        if isinstance(response, dict)
        else getattr(response, "vectors", {})
    )

    chunks = []
    for chunk_id, vector in vectors.items():
        metadata = (
            vector.get("metadata", {})
            if isinstance(vector, dict)
            else getattr(vector, "metadata", {})
        )
        chunks.append({"id": chunk_id, "score": 0.0, "metadata": dict(metadata)})
    return chunks
