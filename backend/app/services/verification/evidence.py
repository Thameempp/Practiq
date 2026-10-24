from fastapi import HTTPException

from app.citations.catalog import attach_sources
from app.citations.models import Source
from app.citations.store import resolve_source, source_for
from app.documents.repository import get_document
from app.orchestration.runtime import check_active
from app.services.pdf_source import original_pages
from app.services.stored_chunks import DocumentStoreError
from app.services.verification.validation import normalized
from app.services.verification.models import VerificationError
from app.services.retrieval.topics import source_in_scope


def confirm_sources(sources: list[Source], target, knowledge_base_id: str) -> tuple[list, list]:
    confirmed, issues, pages, contexts = [], [], {}, {}
    for source in sources:
        check_active()
        if source.document_id not in target.document_ids or source.knowledge_base_id != knowledge_base_id:
            issues.append("A source belongs to a different PDF or knowledge base.")
            continue
        if not source_in_scope(source, target.scope, contexts):
            issues.append(f"Source {source.id} is outside the selected topic or subtopics.")
            continue
        if source.document_id not in pages:
            try:
                pages[source.document_id] = original_pages(source.document_id) or []
            except DocumentStoreError:
                pages[source.document_id] = []
        text = next((p["text"] for p in pages[source.document_id] if p["page"] == source.page), "")
        if (source.page != source.page_end or not source.quote.strip()
                or normalized(source.quote) not in normalized(text)):
            issues.append(f"Source {source.id} could not be confirmed as an exact original-PDF passage.")
            continue
        confirmed.append(source)
    return confirmed, issues


def load_sources(target, knowledge_base_id: str) -> tuple[list, list]:
    sources, issues = [], []
    for source_id in dict.fromkeys(target.source_ids):
        check_active()
        try:
            value = resolve_source(source_id, knowledge_base_id)
            sources.append(Source.model_validate({key: value[key] for key in Source.model_fields if key in value}))
        except HTTPException:
            issues.append(f"Source {source_id} is unavailable or its PDF has changed.")
    confirmed, invalid = confirm_sources(sources, target, knowledge_base_id)
    return confirmed, issues + invalid


def sources_from_chunks(chunks: list[dict], target, knowledge_base_id: str) -> tuple[list, list]:
    allowed = [chunk for chunk in chunks if (chunk.get("metadata") or {}).get("document_id") in target.document_ids]
    sources = [chunk["source"] for chunk in attach_sources(allowed, knowledge_base_id) if chunk.get("source")]
    return confirm_sources(sources, target, knowledge_base_id)


def pinpoint_sources(result, knowledge_base_id: str) -> None:
    available = {value["id"]: Source.model_validate(value) for value in result.sources}
    precise = {}
    for claim in result.claims:
        for reference in claim.evidence:
            check_active()
            source = available[reference.source_id]
            document = get_document(source.document_id, knowledge_base_id)
            if document is None or document.status != "ready":
                raise VerificationError("A source PDF is no longer available. The answer could not be confirmed.")
            record = source_for(document, source.page, reference.quote, chunk_id=source.chunk_id)
            reference.source_id = record.id
            precise[record.id] = record.public()
    result.sources = list(precise.values())
