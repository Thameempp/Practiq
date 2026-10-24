from fastapi import APIRouter

from app.services.understanding.models import DocumentMap
from app.services.understanding.service import document_map

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/{document_id}/map", response_model=DocumentMap)
def get_document_map(document_id: str, knowledge_base_id: str = "local", refresh: bool = False):
    return document_map(document_id, knowledge_base_id, refresh=refresh)
