import hashlib
import json

from fastapi import HTTPException

from app.citations.documents import require_pdf, revision_of
from app.citations.models import Source
from app.documents.database import connection
from app.documents.models import Document


def source_for(document: Document, page: int, quote: str, *,
               chunk_id: str | None = None, page_end: int | None = None) -> Source:
    try:
        _, path = require_pdf(document.document_id, document.knowledge_base_id)
        revision = revision_of(path)
    except HTTPException:
        revision = ""
    identity = [document.knowledge_base_id, document.document_id, chunk_id, page, page_end, quote, revision]
    source_id = "c" + hashlib.sha256(json.dumps(identity).encode()).hexdigest()[:24]
    return Source(id=source_id, knowledge_base_id=document.knowledge_base_id,
                  document_id=document.document_id, chunk_id=chunk_id, filename=document.filename,
                  page=page, page_end=page_end or page, quote=quote, revision=revision)


def save_sources(sources: list[Source]) -> None:
    if not sources:
        return
    with connection() as db:
        db.executemany("INSERT OR IGNORE INTO citation_sources VALUES (?, ?, ?, ?)",
                       [(s.id, s.knowledge_base_id, s.document_id, s.model_dump_json()) for s in sources])


def resolve_source(source_id: str, knowledge_base_id: str) -> dict:
    with connection() as db:
        row = db.execute("SELECT payload FROM citation_sources WHERE id=? AND knowledge_base_id=?",
                         (source_id, knowledge_base_id)).fetchone()
    if row is None:
        raise HTTPException(404, "This source is unavailable.")
    source = Source.model_validate_json(row["payload"])
    document, path = require_pdf(source.document_id, knowledge_base_id)
    if source.page_end > document.pages or (source.revision and source.revision != revision_of(path)):
        raise HTTPException(409, "The source PDF has changed. Ask the question again.")
    return {**source.public(), "page_count": document.pages}
