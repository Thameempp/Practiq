import os
import traceback
from uuid import uuid4
from fastapi import  UploadFile, File, HTTPException, APIRouter
from app.core.config import settings
from app.services.loader import load_pdf
from app.services.chunker import chunk_pages
from app.services.ingestion import ingest_chunks
from app.services.hierarchy_extractor import extract_hierarchy

# router setup
router = APIRouter(
    prefix='/upload',
    tags=["upload"]
)

# folder for uploads
upload_dir = settings.BASE_DIR / "uploads"
os.makedirs(upload_dir, exist_ok=True)

# endpoints
@router.post("/upload-pdf/")
async def upload_file(file: UploadFile = File(...)):
    # validation for file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only Pdf file allowed. "
        )

    # saving the file
    document_id = uuid4().hex
    file_path = os.path.join(upload_dir, file.filename)

    try:
        with open(file_path, "wb") as f:
            while chunk := await file.read(1024*1024):
                f.write(chunk)

        print("pdf upload complete", flush=True)

        # pipeline : load -> clean -> chunker -> ingest
        
        pages, page_count = load_pdf(file_path)
        print("pdf load complete", flush=True)
        chunks = chunk_pages(pages)
        print("chunking complete", flush=True)
        ingest_chunks(chunks, document_id=document_id, filename=file.filename)
        print("ingestion complete", flush=True)
        hierarchy = extract_hierarchy(file_path)
        annotate_hierarchy(hierarchy, document_id, file.filename)
        print("hierarchy extraction complete", flush=True)


    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"failed to process the file: {str(e)}")


    return {
        "document_id": document_id,
        "filename":file.filename,
        "pages": page_count,
        "status":"successfully uploaded",
        "chunks_count":len(chunks),
        "saved_path":str(file_path),
        "hierarchy": hierarchy,
    }


def annotate_hierarchy(nodes, document_id: str, filename: str):
    for node in nodes:
        node["documentId"] = document_id
        node["filename"] = filename
        annotate_hierarchy(node.get("children", []), document_id, filename)
