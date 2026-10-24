from pydantic import BaseModel, Field


class QuestionScope(BaseModel):
    id: str | None = None
    title: str
    type: str | None = None
    documentId: str | None = None
    filename: str | None = None
    page: int | None = None
    pageLabel: str | None = None
    summary: str | None = None
    excerpt: str | None = None
    descendantTitles: list[str] = Field(default_factory=list)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000, pattern=r"\S")
    scope: QuestionScope | None = None
    document_id: str | None = None  # Explicit QA constraint; omit to search the knowledge base.
    knowledge_base_id: str = Field(default="local", min_length=1, max_length=100)
    conversation_id: str | None = Field(default=None, min_length=1, max_length=100)
    document_order: list[str] = Field(default_factory=list, max_length=200)
    selection_id: str | None = None
    outline: list[str] = Field(default_factory=list)
