from typing import Literal

from pydantic import BaseModel, Field


class QueryAnalysis(BaseModel):
    intent: Literal["summarize_document", "summarize_all_documents", "document_qa",
                    "cross_document_qa", "create_study_material", "verify_answer", "document_structure", "other"]
    document_scope: Literal["single", "all", "unspecified"] = "unspecified"
    document_reference: str | None = None
    summary_type: Literal["comprehensive", "key_points", "brief", "chapter"] = "comprehensive"
    chapter_reference: str | None = None
    consolidated: bool = False
    confidence: float = Field(default=1.0, ge=0, le=1)
