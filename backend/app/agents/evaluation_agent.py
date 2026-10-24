"""Validate structure and provenance, then separately review answer support."""

from app.agents.base import BaseAgent
from app.orchestration.runtime import check_active
from app.services.mcq.evaluator import validate_grounding, validate_passages
from app.services.mcq.quality import validate_review
from app.services.mcq.review_prompt import REVIEW_SYSTEM_PROMPT, build_review_prompt
from app.services.mcq.schemas import MCQResponse
from app.services.mcq.validator import MCQValidationError, parse_mcq_response


class EvaluationAgent(BaseAgent[MCQResponse]):
    def __init__(self, generate_text):
        self.generate_text = generate_text


    def evaluate(self, raw_content, passages, *, document_id: str, count: int, previous_questions=()) -> MCQResponse:
        return self.run(raw_content, passages, document_id=document_id, count=count,
                        previous_questions=previous_questions)


    def _run(self, raw_content, passages, *, document_id: str, count: int, previous_questions=()) -> MCQResponse:
        if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 10:
            raise MCQValidationError("The quiz must contain between 1 and 10 questions.")
        validate_passages(passages, document_id)
        draft = parse_mcq_response(raw_content)
        if len(draft.questions) != count:
            raise MCQValidationError(
                f"The quiz service returned {len(draft.questions)} questions instead of {count}."
            )
        result = validate_grounding(draft, passages)
        check_active()
        review = self.generate_text(REVIEW_SYSTEM_PROMPT, build_review_prompt(result, previous_questions))
        check_active()
        validate_review(review, result, require_distinct=bool(previous_questions))
        return result
