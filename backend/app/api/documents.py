import logging

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.documents.migration import adopt_local_document
from app.documents.repository import list_documents

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)


class DocumentSync(BaseModel):
    knowledge_base_id: str = Field(default="local", min_length=1, max_length=100)
    document_ids: list[str] = Field(default_factory=list, max_length=200)


@router.get("")
def documents(knowledge_base_id: str = "local"):
    return {"documents": [doc.model_dump(exclude={"saved_path"}) for doc in list_documents(knowledge_base_id)]}


@router.post("/sync")
def sync_documents(request: DocumentSync):
    missing = []
    for document_id in dict.fromkeys(request.document_ids):
        try:
            adopt_local_document(document_id, request.knowledge_base_id)
        except Exception:
            logger.warning("Could not restore saved document %s", document_id)
            missing.append(document_id)
    return {**documents(request.knowledge_base_id), "missing_document_ids": missing}
