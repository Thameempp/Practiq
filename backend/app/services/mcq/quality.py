"""Fail closed on missing, malformed or negative answer-review verdicts."""

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.services.mcq.schemas import MCQResponse
from app.services.mcq.validator import MCQValidationError
from app.services.mcq.novelty import DuplicateQuestion


class AnswerVerdict(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    question_id: str = Field(min_length=1)
    answer_supported: bool
    explanation_supported: bool
    unambiguous: bool
    distinct: bool | None = None


class AnswerReview(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    verdicts: list[AnswerVerdict] = Field(min_length=1, max_length=10)


def validate_review(raw, result: MCQResponse, *, require_distinct=False) -> None:
    try:
        review = (AnswerReview.model_validate_json(raw) if isinstance(raw, str)
                  else AnswerReview.model_validate(raw))
    except (ValidationError, ValueError, TypeError) as error:
        raise MCQValidationError("The quiz answer review returned an invalid response.") from error
    ids = [verdict.question_id for verdict in review.verdicts]
    if len(ids) != len(set(ids)) or set(ids) != {q.id for q in result.questions}:
        raise MCQValidationError("The quiz answer review did not cover every question.")
    if require_distinct and any(verdict.distinct is not True for verdict in review.verdicts):
        raise DuplicateQuestion([question.question for question in result.questions])
    if any(not (v.answer_supported and v.explanation_supported and v.unambiguous)
           for v in review.verdicts):
        raise MCQValidationError(
            "The quiz contained an ambiguous question or an answer/explanation that "
            "was not supported by its PDF quotes. Please try again."
        )
