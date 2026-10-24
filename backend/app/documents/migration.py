"""Adopt older local uploads by reading server metadata, never browser filenames."""

from app.documents.models import Document
from app.documents.repository import get_document, save_document
from app.services.pinecone_index import get_index
from app.services.stored_chunks import read_stored_chunks


def adopt_local_document(document_id, knowledge_base_id="local"):
    if get_document(document_id, knowledge_base_id):
        return
    # Untagged historical uploads only belong to the existing local knowledge base.
    if knowledge_base_id != "local":
        raise ValueError("This PDF is not registered in this knowledge base.")
    chunks = read_stored_chunks(document_id, get_index())
    if not chunks:
        raise ValueError("This saved PDF is no longer available. Upload it again.")
    metadata = [chunk["metadata"] for chunk in chunks]
    if any(item.get("knowledge_base_id", "local") != knowledge_base_id for item in metadata):
        raise ValueError("This PDF belongs to another knowledge base.")
    filename = metadata[0].get("filename") or "Uploaded PDF"
    pages = max(int(item.get("page", 0)) for item in metadata)
    save_document(Document(document_id=document_id, filename=filename, status="ready",
                           pages=pages, chunks=len(chunks), knowledge_base_id=knowledge_base_id))
