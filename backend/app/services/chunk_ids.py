from numbers import Number
from typing import Any

CHUNK_ID_PREFIX = "chunk-"


def make_chunk_id(document_id: str | None, index: int) -> str:
    if document_id:
        return f"{document_id}-chunk-{index}"
    return f"{CHUNK_ID_PREFIX}{index}"


def document_id_of(chunk: dict[str, Any]) -> str | None:
    document_id = (chunk.get("metadata") or {}).get("document_id")
    return str(document_id) if document_id else None


def chunk_index_of(chunk: dict[str, Any]) -> int | None:
    metadata_index = _to_int((chunk.get("metadata") or {}).get("chunk_index"))
    if metadata_index is not None:
        return metadata_index

    chunk_id = chunk.get("id")
    if isinstance(chunk_id, str) and chunk_id.startswith(CHUNK_ID_PREFIX):
        return _to_int(chunk_id[len(CHUNK_ID_PREFIX):])

    return None


def _to_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, Number) and float(value).is_integer():
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None
