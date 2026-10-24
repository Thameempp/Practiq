from pydantic import BaseModel, Field


class Source(BaseModel):
    id: str
    knowledge_base_id: str
    document_id: str
    chunk_id: str | None = None
    filename: str
    page: int = Field(ge=1)
    page_end: int = Field(ge=1)
    quote: str
    revision: str = ""


    def public(self) -> dict:
        return {**self.model_dump(exclude={"revision"}), "page_index": self.page - 1}


class SourceDetails(BaseModel):
    id: str
    knowledge_base_id: str
    document_id: str
    chunk_id: str | None = None
    filename: str
    page: int = Field(ge=1)
    page_end: int = Field(ge=1)
    page_index: int = Field(ge=0)
    page_count: int = Field(ge=1)
    quote: str
