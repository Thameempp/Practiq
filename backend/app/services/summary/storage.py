"""Adapt complete stored document chunks to the summary agent's input format."""

from app.services.pinecone_index import get_index
from app.services.stored_chunks import DocumentStoreError, read_stored_chunks
from app.services.summary.models import SummaryError
from app.services.pdf_source import original_pages, complete_chunks


def load_summary_chunks(document_id: str) -> list[dict]:
    if not document_id:
        raise SummaryError("Choose an uploaded PDF before requesting a summary.")
    try:
        pages = original_pages(document_id)
        if pages is not None:
            return pages
        chunks = read_stored_chunks(document_id, get_index())
        if not complete_chunks(chunks, document_id):
            raise DocumentStoreError("The indexed PDF is incomplete. Upload the original PDF again.")
    except DocumentStoreError as error:
        raise SummaryError(str(error)) from error
    return [{"text": chunk["metadata"].get("text", ""),
             "page": chunk["metadata"].get("page")} for chunk in chunks]
