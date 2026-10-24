"""Existing PDF extraction/indexing with registry lifecycle metadata."""

from app.documents.repository import save_document
from app.services.chunker import chunk_pages
from app.services.hierarchy_extractor import extract_hierarchy
from app.services.ingestion import ingest_chunks
from app.services.loader import load_pdf
from app.services.understanding.service import analyze_document


def annotate_hierarchy(nodes, document_id, filename):
    for node in nodes:
        node.update(documentId=document_id, filename=filename)
        annotate_hierarchy(node.get("children", []), document_id, filename)


def process_document(document):
    pages, page_count = load_pdf(document.saved_path)
    chunks = chunk_pages(pages)
    hierarchy = extract_hierarchy(document.saved_path)
    annotate_hierarchy(hierarchy, document.document_id, document.filename)
    document.pages, document.chunks, document.hierarchy = page_count, len(chunks), hierarchy
    analyze_document(document, pages=pages)
    hierarchy = document.hierarchy
    ingest_chunks(chunks, document_id=document.document_id, filename=document.filename,
                  knowledge_base_id=document.knowledge_base_id)
    document.status, document.pages, document.chunks = "ready", page_count, len(chunks)
    document.hierarchy = hierarchy
    save_document(document)
    return {"document_id": document.document_id, "filename": document.filename,
            "pages": page_count, "status": "ready", "chunks_count": len(chunks),
            "saved_path": document.saved_path, "hierarchy": hierarchy}
