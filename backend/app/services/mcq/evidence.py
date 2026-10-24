"""Prepare the exact, page-addressable PDF passages available to the quiz model."""

from dataclasses import dataclass

from app.orchestration.runtime import check_active
from app.services.mcq.errors import MCQGenerationError
from app.services.context import (
    MAX_CHUNK_TEXT_CHARS_FOR_LLM,
    MAX_CONTEXT_CHUNKS_FOR_LLM,
    MAX_TOTAL_CONTEXT_CHARS_FOR_LLM,
)


@dataclass(frozen=True)
class EvidencePassage:
    source_id: str
    document_id: str
    filename: str
    page: int
    text: str


def retrieve_passages(retrieve_context, document_id: str, scope) -> list[EvidencePassage]:
    try:
        chunks = retrieve_context((scope or {}).get("title") or "the selected document section",
                                  scope=scope, document_id=document_id)
    except ValueError as error:
        raise MCQGenerationError(str(error)) from error
    check_active()
    return prepare_evidence(chunks, document_id)


def prepare_evidence(chunks, document_id: str) -> list[EvidencePassage]:
    passages = []
    remaining_chars = MAX_TOTAL_CONTEXT_CHARS_FOR_LLM
    for chunk in chunks:
        metadata = chunk.get("metadata") or {}
        if metadata.get("document_id") != document_id:
            continue
        page = _page_number(metadata.get("page"))
        text = str(metadata.get("text") or chunk.get("text") or "").strip()
        if page is None or not text:
            continue

        text = text[:min(MAX_CHUNK_TEXT_CHARS_FOR_LLM, remaining_chars)]
        passages.append(EvidencePassage(
            source_id=f"s{len(passages) + 1}",
            document_id=document_id,
            filename=str(metadata.get("filename") or "Uploaded PDF"),
            page=page,
            text=text,
        ))
        remaining_chars -= len(text)
        if len(passages) >= MAX_CONTEXT_CHUNKS_FOR_LLM or remaining_chars <= 0:
            break
    return passages


def _page_number(value) -> int | None:
    # Pinecone may return integer metadata as floats. Reject fractional/unknown pages.
    if isinstance(value, bool):
        return None
    try:
        page = int(value)
        return page if page >= 1 and float(value) == page else None
    except (TypeError, ValueError, OverflowError):
        return None
