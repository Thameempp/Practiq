from app.services.chunk_ids import chunk_index_of, document_id_of, make_chunk_id
from app.services.chunk_store import get_chunks_by_indexes, get_current_chunks

MAX_CONTEXT_CHUNKS_FOR_LLM = 8
MAX_CHUNK_TEXT_CHARS_FOR_LLM = 1400
MAX_TOTAL_CONTEXT_CHARS_FOR_LLM = 7000


def normalize_question(user_question: str) -> tuple[str, str | None]:
    """Remove frontend-only scope decoration from the question."""
    normalized_question = user_question.strip()
    scope = None

    if normalized_question.startswith("[Scope:"):
        closing_bracket = normalized_question.find("]")
        if closing_bracket != -1:
            scope = normalized_question[len("[Scope:"):closing_bracket].strip()
            normalized_question = normalized_question[closing_bracket + 1:].strip()

    return normalized_question, scope


def build_retrieved_context(
    chunks,
    max_chunks: int = MAX_CONTEXT_CHUNKS_FOR_LLM,
    max_total_chars: int = MAX_TOTAL_CONTEXT_CHARS_FOR_LLM,
) -> str:
    """Format reranked chunks for the answer model."""
    if not chunks:
        return "[No relevant text found in the document]"

    formatted_chunks = []
    total_chars = 0
    for chunk in chunks[:max_chunks]:
        metadata = chunk.get("metadata") or {}
        page = metadata.get("page", "unknown")
        filename = metadata.get("filename", "unknown document")
        text = str(metadata.get("text") or chunk.get("text", "")).strip()
        if not text:
            continue

        remaining_chars = max_total_chars - total_chars
        if remaining_chars <= 0:
            break

        text = text[:min(MAX_CHUNK_TEXT_CHARS_FOR_LLM, remaining_chars)]
        formatted_chunks.append(f"[document {filename}, page {page}]\n{text}")
        total_chars += len(text)

    return "\n\n".join(formatted_chunks)


def expand_with_neighbor_chunks(chunks, window: int = 1, max_chunks: int = 8):
    """Include adjacent chunks so headings bring their following content."""
    indexes_by_doc, direct_chunks = _neighbor_indexes(chunks, window)

    expanded = {}
    for document_id, indexes in indexes_by_doc.items():
        for chunk in get_chunks_by_indexes(sorted(set(indexes)), document_id=document_id):
            expanded[chunk.get("id") or _fallback_chunk_id(chunk)] = chunk

    if not expanded:
        expanded.update(_neighbors_from_memory(indexes_by_doc))

    expanded.update(direct_chunks)

    for chunk in chunks:
        chunk_id = chunk.get("id")
        if chunk_id and chunk_id not in expanded:
            expanded[chunk_id] = chunk

    return list(expanded.values())[:max_chunks]


def _neighbor_indexes(chunks, window: int):
    indexes_by_doc: dict[str | None, list[int]] = {}
    direct_chunks = {}

    for chunk in chunks:
        chunk_index = chunk_index_of(chunk)
        if chunk_index is None:
            if chunk.get("id"):
                direct_chunks[chunk["id"]] = chunk
            continue

        indexes = indexes_by_doc.setdefault(document_id_of(chunk), [])
        indexes.extend(
            index
            for index in range(chunk_index - window, chunk_index + window + 1)
            if index >= 0
        )

    return indexes_by_doc, direct_chunks


def _neighbors_from_memory(indexes_by_doc):
    by_index = {
        (document_id_of(chunk), chunk_index_of(chunk)): chunk
        for document_id in indexes_by_doc
        for chunk in get_current_chunks(document_id)
        if chunk_index_of(chunk) is not None
    }

    found = {}
    for document_id, indexes in indexes_by_doc.items():
        for index in sorted(set(indexes)):
            chunk = by_index.get((document_id, index))
            if chunk:
                found[chunk.get("id") or _fallback_chunk_id(chunk)] = chunk
    return found


def _fallback_chunk_id(chunk) -> str:
    chunk_index = chunk_index_of(chunk)
    if chunk_index is None:
        return "chunk-unknown"
    return make_chunk_id(document_id_of(chunk), chunk_index)
