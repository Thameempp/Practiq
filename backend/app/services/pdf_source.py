"""Complete local sources for document IDs already resolved by the orchestrator."""

from functools import lru_cache

import pymupdf
from fastapi import HTTPException

from app.citations.documents import require_pdf, revision_of
from app.documents.database import connection
from app.documents.models import Document
from app.orchestration.runtime import check_active
from app.orchestration.errors import TaskCancelled, TaskDeadline
from app.services.stored_chunks import DocumentStoreError


def registered_document(document_id: str) -> Document | None:
    # IDs are globally unique. Public routes must still resolve membership first.
    with connection() as db:
        row = db.execute("SELECT payload FROM documents WHERE document_id=?", (document_id,)).fetchone()
    return Document.model_validate_json(row["payload"]) if row else None


def original_pages(document_id: str) -> list[dict] | None:
    check_active()
    document = registered_document(document_id)
    if document is None:
        return None
    try:
        _, path = require_pdf(document_id, document.knowledge_base_id)
    except HTTPException as error:
        if error.status_code == 404:
            return None
        raise DocumentStoreError("The PDF is not ready to read.") from error
    texts = _extract(str(path), revision_of(path))
    check_active()
    return [{"page": number, "text": text} for number, text in enumerate(texts, 1)]


@lru_cache(maxsize=4)
def _extract(path: str, revision: str) -> tuple[str, ...]:
    texts = []
    try:
        with pymupdf.open(path) as pdf:
            for page in pdf:
                check_active()
                texts.append(page.get_text("text", sort=True))
    except (TaskCancelled, TaskDeadline):
        raise
    except (OSError, RuntimeError) as error:
        raise DocumentStoreError("The original PDF could not be read. Please upload it again.") from error
    return tuple(texts)


def complete_chunks(chunks: list[dict], document_id: str) -> bool:
    document = registered_document(document_id)
    if document is None:
        return bool(chunks)
    if document.chunks < 1:
        return False
    ids = {chunk.get("id") for chunk in chunks}
    return ids == {f"{document_id}-chunk-{index}" for index in range(document.chunks)}
