"""Rebuild the complete lexical corpus with the ingestion pipeline's existing IDs."""

from app.services.chunker import chunk_pages
from app.services.chunk_ids import make_chunk_id
from app.services.page_noise import clean_pages
from app.services.pdf_source import original_pages, registered_document


def original_chunks(document_id: str) -> list[dict] | None:
    pages = original_pages(document_id)
    if pages is None:
        return None
    document = registered_document(document_id)
    return [{"id": make_chunk_id(document_id, index), "score": 0.0, "metadata": {
        "document_id": document_id, "knowledge_base_id": document.knowledge_base_id,
        "filename": document.filename, "chunk_index": index,
        "page": chunk["page"], "text": chunk["text"],
    }} for index, chunk in enumerate(chunk_pages(clean_pages(pages)))]
