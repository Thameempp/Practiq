from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


OptionKey = Literal["A", "B", "C", "D"]


class TextModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class MCQOption(TextModel):
    key: OptionKey
    text: str = Field(min_length=1, max_length=500)
    isCorrect: bool = False


class MCQEvidence(TextModel):
    source_id: str = Field(min_length=1)
    quote: str = Field(min_length=20, max_length=1400)


class MCQSource(TextModel):
    citation_id: str | None = None
    knowledge_base_id: str = "local"
    document_id: str
    filename: str
    page: int = Field(ge=1)
    quote: str


class MCQQuestionContent(TextModel):
    id: str = Field(min_length=1, max_length=80)
    question: str = Field(min_length=1, max_length=1000)
    options: list[MCQOption] = Field(min_length=4, max_length=4)
    explanation: str = Field(min_length=1, max_length=1200)


    @model_validator(mode="after")
    def validate_options(self):
        keys = [option.key for option in self.options]
        if keys != ["A", "B", "C", "D"]:
            raise ValueError("options must contain keys A, B, C, and D in order")
        if sum(option.isCorrect for option in self.options) != 1:
            raise ValueError("each question must have exactly one correct option")
        texts = [" ".join(option.text.casefold().split()) for option in self.options]
        if len(set(texts)) != 4:
            raise ValueError("answer options must have distinct text")
        return self


class MCQDraftQuestion(MCQQuestionContent):
    evidence: list[MCQEvidence] = Field(min_length=1, max_length=4)


class MCQDraftResponse(BaseModel):
    questions: list[MCQDraftQuestion] = Field(min_length=1, max_length=10)


class MCQQuestion(MCQQuestionContent):
    sources: list[MCQSource] = Field(min_length=1, max_length=4)


class MCQResponse(BaseModel):
    questions: list[MCQQuestion] = Field(min_length=1, max_length=10)


class MCQRequest(BaseModel):
    knowledge_base_id: str = Field(default="local", min_length=1)
    document_id: str = Field(min_length=1)
    scope: dict | None = None
    count: int = Field(default=5, ge=1, le=10)
    exclude_questions: list[str] = Field(default_factory=list, max_length=100)


    @model_validator(mode="after")
    def validate_exclusions(self):
        if any(not text.strip() or len(text) > 1000 for text in self.exclude_questions):
            raise ValueError("Excluded questions must contain 1-1000 characters.")
        return self
