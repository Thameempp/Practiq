from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.orchestration.errors import TaskFailure

Verdict = Literal["supported", "contradicted", "partially_supported",
                  "insufficient_evidence", "conflicting_sources"]
Identifier = Annotated[str, Field(min_length=1, max_length=120)]


class VerificationError(TaskFailure):
    pass


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)


class VerificationTarget(StrictModel):
    response_id: str = Field(default="", max_length=120)
    question: str = Field(min_length=1, max_length=4000)
    answer: str = Field(min_length=1, max_length=40000)
    document_ids: list[Identifier] = Field(min_length=1, max_length=200)
    source_ids: list[Identifier] = Field(default_factory=list, max_length=32)
    objection: str = Field(default="", max_length=4000)
    artifact: Literal["answer", "summary", "mcq"] = "answer"
    scope: dict | None = None
    truncated: bool = False


class Claim(StrictModel):
    id: str = Field(min_length=1, max_length=30)
    text: str = Field(min_length=1, max_length=1800)


class ClaimSet(StrictModel):
    claims: list[Claim] = Field(min_length=1, max_length=8)
    complete: bool


class EvidenceReference(StrictModel):
    source_id: str
    quote: str = Field(min_length=10, max_length=800)
    stance: Literal["supports", "contradicts"]


class ClaimVerdict(StrictModel):
    claim_id: str
    verdict: Verdict
    reason: str = Field(min_length=1, max_length=700)
    correction: str = Field(default="", max_length=1800)
    evidence: list[EvidenceReference] = Field(default_factory=list, max_length=6)


class Review(StrictModel):
    claims: list[ClaimVerdict] = Field(min_length=1, max_length=8)


class VerificationResult(StrictModel):
    response_id: str
    original_response_id: str
    verdict: Verdict
    initial_verdict: Verdict
    claims: list[ClaimVerdict]
    claim_texts: dict[str, str]
    sources: list[dict]
    corrected_answer: str | None = None
    limitations: list[str] = Field(default_factory=list)
    citation_issues: list[str] = Field(default_factory=list)
    retrieval_rounds: int = 0
    coverage_complete: bool = False
    scope: dict | None = None
