from typing import Literal

from pydantic import BaseModel, Field

DetectionStatus = Literal["confirmed", "probable", "uncertain", "not_found"]


class MapIssue(BaseModel):
    code: str
    message: str
    pdf_page: int | None = None


class PageElement(BaseModel):
    kind: str
    status: DetectionStatus = "probable"
    bbox: list[float] = Field(default_factory=list)
    text: str = ""


class PageInventory(BaseModel):
    pdf_page: int = Field(ge=1)
    printed_page: str | None = None
    printed_label_source: Literal["pdf_labels", "footer"] | None = None
    width: float = 0
    height: float = 0
    rotation: int = 0
    text_chars: int = 0
    image_count: int = 0
    vector_count: int = 0
    needs_ocr: bool = False
    quality: Literal["readable", "scanned_candidate", "blank_candidate", "unreadable", "failed"] = "readable"
    duplicate_of: int | None = None
    elements: list[PageElement] = Field(default_factory=list)
    issues: list[MapIssue] = Field(default_factory=list)
