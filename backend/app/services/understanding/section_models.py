from pydantic import BaseModel, Field

from app.services.understanding.page_models import DetectionStatus


class DocumentSection(BaseModel):
    section_id: str
    title: str
    section_type: str
    roles: list[str] = Field(default_factory=list)
    start_page: int | None = None
    end_page: int | None = None
    printed_page: str | None = None
    parent_section_id: str | None = None
    children: list[str] = Field(default_factory=list)
    status: DetectionStatus = "uncertain"
    confidence: float = Field(default=0, ge=0, le=1)
    evidence: str = ""


class DocumentTopic(BaseModel):
    topic_id: str
    label: str
    section_id: str | None = None
    chapter_id: str | None = None
    pdf_page: int = Field(ge=1)
    kind: str = "heading"
    status: DetectionStatus = "probable"
    evidence: str = ""
    chunk_ids: list[str] = Field(default_factory=list)
