"""Resolve model citations against supplied evidence, never model-written pages."""

from app.services.mcq.evidence import EvidencePassage
from app.services.mcq.schemas import (
    MCQDraftResponse,
    MCQQuestion,
    MCQResponse,
    MCQSource,
)
from app.services.mcq.validator import MCQValidationError


def validate_passages(passages: list[EvidencePassage], document_id: str) -> None:
    if not isinstance(document_id, str) or not document_id.strip():
        raise MCQValidationError("A document ID is required to evaluate PDF evidence.")
    ids = [passage.source_id for passage in passages]
    if not passages or len(ids) != len(set(ids)):
        raise MCQValidationError("The quiz requires unique, page-addressable PDF evidence.")
    if any(p.document_id != document_id or not p.source_id or not p.text.strip()
           or isinstance(p.page, bool) or not isinstance(p.page, int) or p.page < 1
           for p in passages):
        raise MCQValidationError("The quiz evidence does not belong to the selected PDF.")


def validate_grounding(
    draft: MCQDraftResponse, passages: list[EvidencePassage]
) -> MCQResponse:
    by_id = {passage.source_id: passage for passage in passages}
    questions = []
    for question in draft.questions:
        sources = []
        for evidence in question.evidence:
            passage = by_id.get(evidence.source_id)
            quote = " ".join(evidence.quote.split())
            if passage is None or not quote or quote not in " ".join(passage.text.split()):
                raise MCQValidationError(
                    "The quiz contained a source quote that could not be verified in the PDF. "
                    "Please regenerate the questions."
                )
            source = MCQSource(
                document_id=passage.document_id,
                filename=passage.filename,
                page=passage.page,
                quote=quote,
            )
            if source not in sources:
                sources.append(source)
        questions.append(MCQQuestion(
            **question.model_dump(exclude={"evidence"}), sources=sources
        ))
    return MCQResponse(questions=questions)
