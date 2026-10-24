import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.documents.deletion import delete_document_data
from app.documents.models import Document
from app.documents.repository import get_document, save_document
from app.services.chunk_store import remove_chunks
from app.services.pinecone_index import get_index
from app.services.upload_pipeline import annotate_hierarchy, process_document

router = APIRouter(prefix="/upload", tags=["upload"])
logger = logging.getLogger(__name__)
upload_dir = settings.BASE_DIR / "uploads"
upload_dir.mkdir(parents=True, exist_ok=True)


@router.post("/upload-pdf/")
async def upload_file(file: UploadFile = File(...), knowledge_base_id: str = Form("local")):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    document_id = uuid4().hex
    document = Document(document_id=document_id, knowledge_base_id=knowledge_base_id,
                        filename=Path(file.filename or "Uploaded PDF.pdf").name,
                        saved_path=str(upload_dir / f"{document_id}.pdf"))
    save_document(document)
    try:
        with open(document.saved_path, "wb") as target:
            while data := await file.read(1024 * 1024):
                target.write(data)
        return await run_in_threadpool(process_document, document)
    except Exception as error:
        document.status = "failed"
        save_document(document)
        logger.exception("PDF upload failed")
        raise HTTPException(status_code=500, detail="Could not process the PDF. Please retry the upload.") from error
    finally:
        await file.close()


@router.delete("/{document_id}")
def delete_document(document_id: str, knowledge_base_id: str = "local"):
    document = get_document(document_id, knowledge_base_id)
    if document is None:
        raise HTTPException(status_code=404, detail="PDF not found in this knowledge base.")
    if document.status == "processing":
        raise HTTPException(status_code=409, detail="Wait for this PDF to finish indexing before removing it.")
    delete_document_data(document, get_index(), upload_dir, remove_chunks)
    return {"document_id": document_id, "status": "deleted"}
