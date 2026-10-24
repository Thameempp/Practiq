from fastapi import APIRouter, Query, Response
from fastapi.responses import FileResponse

from app.citations.documents import require_pdf
from app.citations.models import SourceDetails
from app.citations.store import resolve_source

router = APIRouter(tags=["sources"])


@router.get("/documents/{document_id}/pdf")
def original_pdf(document_id: str, knowledge_base_id: str = Query(default="local", max_length=100)) -> FileResponse:
    document, path = require_pdf(document_id, knowledge_base_id)
    return FileResponse(path, media_type="application/pdf", filename=document.filename,
                        content_disposition_type="inline", headers={
                            "Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff",
                        })


@router.get("/citations/{source_id}", response_model=SourceDetails)
def citation(source_id: str, response: Response, knowledge_base_id: str = Query(default="local", max_length=100)) -> dict:
    response.headers["Cache-Control"] = "private, no-store"
    return resolve_source(source_id, knowledge_base_id)
