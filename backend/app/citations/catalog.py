from typing import Any

from app.citations.store import source_for, save_sources
from app.documents.repository import get_document
from app.orchestration.runtime import current_task


def emit_metadata(kind: str, data: Any) -> None:
    context = current_task.get()
    if context is not None:
        context.check()
        context.send(kind, data)


def attach_sources(chunks: list[dict], knowledge_base_id: str) -> list[dict]:
    result, documents = [], {}
    for chunk in chunks:
        chunk = {key: value for key, value in chunk.items() if key != "source"}
        metadata = chunk.get("metadata") or {}
        document_id = metadata.get("document_id")
        if document_id not in documents:
            documents[document_id] = get_document(document_id, knowledge_base_id)
        document = documents[document_id]
        page, end = chunk.get("page_start", 0), chunk.get("page_end", 0)
        if document and document.status == "ready" and 1 <= page == end <= document.pages:
            source = source_for(document, page, chunk["text"], chunk_id=chunk.get("id"))
            result.append({**chunk, "source": source})
        else:
            result.append(chunk)
    return result


def publish_sources(chunks: list[dict]) -> dict:
    sources = {chunk["source"].id: chunk["source"] for chunk in chunks if chunk.get("source")}
    save_sources(list(sources.values()))
    public = {key: {**source.public(), "label": str(index)}
              for index, (key, source) in enumerate(sources.items(), 1)}
    if public:
        emit_metadata("sources", list(public.values()))
    return public
