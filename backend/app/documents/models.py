from typing import Literal

from pydantic import BaseModel, Field


class Document(BaseModel):
    document_id: str
    knowledge_base_id: str = "local"
    filename: str
    status: Literal["processing", "ready", "failed"] = "processing"
    pages: int = 0
    chunks: int = 0
    hierarchy: list[dict] = Field(default_factory=list)
    saved_path: str | None = None


class DocumentResolution(BaseModel):
    status: Literal["resolved", "all_documents", "clarification_required", "not_found",
                    "processing", "no_documents"]
    document_ids: list[str] = Field(default_factory=list)
    clarification_message: str | None = None
    candidate_document_ids: list[str] = Field(default_factory=list)
