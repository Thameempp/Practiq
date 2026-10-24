"""Normalize evidence and reject chunks outside the requested document."""

import math
from collections.abc import Mapping

from app.services.chunk_ids import chunk_index_of


def clean_candidates(chunks, document_id: str) -> list[dict]:
    found = {}
    for chunk in chunks:
        if not isinstance(chunk, Mapping):
            continue
        metadata = chunk.get("metadata") or {}
        if not isinstance(metadata, Mapping) or metadata.get("document_id") != document_id:
            continue
        text = metadata.get("text") or chunk.get("text")
        chunk_id = chunk.get("id")
        start = _integer(metadata.get("page_start", metadata.get("page")))
        end = _integer(metadata.get("page_end", start))
        if not isinstance(text, str) or not text.strip() or not isinstance(chunk_id, str) or not chunk_id:
            continue
        if start is None or end is None or start < 1 or end < start:
            continue
        chunk_index = chunk_index_of(chunk)
        prefix = f"{document_id}-chunk-"
        if chunk_index is None and chunk_id.startswith(prefix):
            chunk_index = _integer(chunk_id[len(prefix):])
        score = finite_score(chunk.get("score", 0))
        found.setdefault(chunk_id, {
            "id": chunk_id, "text": text.strip(), "page_start": start, "page_end": end,
            "chunk_index": chunk_index, "score": score if score is not None else 0.0,
            "metadata": {**metadata, "text": text.strip(), "page": start},
        })
    return list(found.values())


def finite_score(value) -> float | None:
    try:
        score = float(value)
        return score if not isinstance(value, bool) and math.isfinite(score) else None
    except (ValueError, TypeError, OverflowError):
        return None


def _integer(value) -> int | None:
    number = finite_score(value)
    return int(number) if number is not None and number.is_integer() else None
