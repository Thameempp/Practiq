from typing import Literal

from pydantic import BaseModel, Field

from app.services.understanding.page_models import DetectionStatus, MapIssue, PageInventory
from app.services.understanding.section_models import DocumentSection, DocumentTopic

MAP_VERSION = 2


class DocumentMap(BaseModel):
    document_id: str
    knowledge_base_id: str = "local"
    filename: str
    file_type: str = "application/pdf"
    title: str | None = None
    author: str | None = None
    language: str | None = None
    total_pdf_pages: int = Field(ge=0)
    revision: str
    hierarchy_signature: str
    analysis_version: int = MAP_VERSION
    topic_index_version: int
    embedded_outline: bool = False
    has_table_of_contents: bool = False
    has_subject_index: bool = False
    table_of_contents_status: DetectionStatus = "not_found"
    subject_index_status: DetectionStatus = "not_found"
    structure_status: Literal["processing", "complete", "partial", "failed"] = "processing"
    pages: list[PageInventory] = Field(default_factory=list)
    sections: list[DocumentSection] = Field(default_factory=list)
    topics: list[DocumentTopic] = Field(default_factory=list)
    issues: list[MapIssue] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=lambda: [
        "OCR and semantic interpretation of diagrams are not performed.",
        "Missing physical pages cannot be established from the PDF alone.",
        "Confidence scores are rule-based indicators, not calibrated probabilities.",
    ])
