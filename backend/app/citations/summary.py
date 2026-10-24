from app.citations.catalog import emit_metadata
from app.citations.store import save_sources, source_for
from app.documents.repository import get_document
from app.documents.models import Document


def summary_source(document: Document, result: dict) -> str:
    document = get_document(document.document_id, getattr(document, "knowledge_base_id", "local"))
    if document is None or document.status != "ready":
        return ""
    ranges = [(note["page_start"], note["page_end"]) for note in result.get("chunk_summaries", [])]
    if not ranges:
        return ""
    start, end = min(p[0] for p in ranges), max(p[1] for p in ranges)
    if not 1 <= start <= end <= document.pages:
        return ""
    source = source_for(document, start, "", page_end=end)
    save_sources([source])
    label = f"PDF page {start}" if start == end else f"PDF pages {start}–{end}"
    emit_metadata("sources", [{**source.public(), "label": label}])
    emit_metadata("citation", {"id": source.id, "label": label})
    return f"\n\nOpen source: [{label}](#source-{source.id})\n"
