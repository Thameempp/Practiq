from pathlib import Path

from fastapi import HTTPException

from app.core.config import settings
from app.documents.repository import get_document
from app.documents.models import Document

UPLOAD_DIR = settings.BASE_DIR / "uploads"


def require_pdf(document_id: str, knowledge_base_id: str) -> tuple[Document, Path]:
    document = get_document(document_id, knowledge_base_id)
    if document is None:
        raise HTTPException(404, "This PDF is no longer in the knowledge base.")
    if document.status != "ready":
        raise HTTPException(409, "This PDF is not ready to view.")
    path = (Path(document.saved_path) if document.saved_path else UPLOAD_DIR / f"{document.document_id}.pdf").resolve()
    if path.parent != UPLOAD_DIR.resolve() or path.suffix.lower() != ".pdf" or not path.is_file():
        raise HTTPException(404, "The original PDF is unavailable. Upload it again.")
    return document, path


def revision_of(path: Path) -> str:
    info = path.stat()
    return f"{info.st_size}:{info.st_mtime_ns}"
