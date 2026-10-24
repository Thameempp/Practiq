from pathlib import Path

from app.documents.repository import delete_record, list_documents


def delete_document_data(document, index, upload_dir, remove_chunks):
    ids = []
    for page in index.list(prefix=f"{document.document_id}-chunk-"):
        items = page if isinstance(page, list) else getattr(page, "vectors", [])
        ids.extend(item if isinstance(item, str) else item.id for item in items)
    for start in range(0, len(ids), 100):
        index.delete(ids=ids[start:start + 100])
    remove_chunks(document.document_id)
    path = Path(document.saved_path) if document.saved_path else upload_dir / Path(document.filename).name
    others = list_documents(document.knowledge_base_id)
    shared = any(doc.document_id != document.document_id and doc.saved_path == document.saved_path
                 and (doc.saved_path or doc.filename == document.filename) for doc in others)
    if not shared and path.resolve().parent == upload_dir.resolve():
        path.unlink(missing_ok=True)
    delete_record(document.document_id, document.knowledge_base_id)
