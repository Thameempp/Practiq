import json
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

from fastapi import HTTPException

from app.citations.documents import require_pdf, revision_of
from app.documents.database import connection
from app.services.page_noise import clean_pages
from app.services.pdf_source import original_pages, registered_document
from app.services.topics.builder import TOPIC_VERSION, build_topic_index


def signature(hierarchy: list[dict]) -> str:
    return sha256(json.dumps(hierarchy, sort_keys=True).encode()).hexdigest()


def save_topics(document, pages: list[dict] | None, revision: str | None = None, *, index=None) -> dict:
    index = index if index is not None else build_topic_index(document.hierarchy, pages, document.pages)
    index.update(signature=signature(document.hierarchy),
                 revision=revision if revision is not None else revision_of(Path(document.saved_path)))
    with connection() as db:
        db.execute("INSERT OR REPLACE INTO document_topics VALUES (?, ?, ?)",
                   (document.document_id, document.knowledge_base_id, json.dumps(index)))
    return index


@lru_cache(maxsize=4)
def _pages(document_id: str, revision: str) -> tuple[list[dict], dict]:
    pages = original_pages(document_id)
    pages = clean_pages(pages) if pages is not None else []
    return pages, {page["page"]: page["text"].split() for page in pages}


def load_topics(document_id: str):
    document = registered_document(document_id)
    if document is None or not document.hierarchy:
        return None
    with connection() as db:
        row = db.execute("SELECT payload FROM document_topics WHERE document_id=? AND knowledge_base_id=?",
                         (document_id, document.knowledge_base_id)).fetchone()
    stored = json.loads(row["payload"]) if row else None
    try:
        _, path = require_pdf(document_id, document.knowledge_base_id)
        revision = revision_of(path)
    except HTTPException:
        revision = ""
    valid = (stored and stored.get("version") == TOPIC_VERSION
             and stored.get("signature") == signature(document.hierarchy))
    pages, words = _pages(document_id, revision) if revision else ([], {})
    if pages and (not valid or stored.get("revision") != revision):
        stored = save_topics(document, pages, revision)
    elif not valid:
        return None
    return stored, words
