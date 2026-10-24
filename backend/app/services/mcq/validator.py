from typing import Any

from pydantic import ValidationError

from app.services.mcq.schemas import MCQDraftResponse


class MCQValidationError(ValueError):
    """Raised when the model response is not a valid MCQ payload."""


def parse_mcq_response(raw_content: str | dict[str, Any]) -> MCQDraftResponse:
    try:
        if isinstance(raw_content, str):
            result = MCQDraftResponse.model_validate_json(raw_content)
        else:
            result = MCQDraftResponse.model_validate(raw_content)
        ids = [question.id for question in result.questions]
        if len(ids) != len(set(ids)):
            raise ValueError("question ids must be unique")
        questions = [" ".join(q.question.casefold().split()) for q in result.questions]
        if len(questions) != len(set(questions)):
            raise ValueError("question text must be unique")
        return result
    except (ValidationError, TypeError, ValueError) as error:
        raise MCQValidationError("The model returned an invalid MCQ payload.") from error
