"""Coordinate scoped retrieval, structured generation and mandatory evaluation."""

from app.agents.base import BaseAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.orchestration.errors import TaskCancelled, TaskDeadline
from app.orchestration.runtime import check_active
from app.services.mcq.errors import MCQGenerationError
from app.services.mcq.evidence import retrieve_passages
from app.services.mcq.prompts import MCQ_SYSTEM_PROMPT, build_mcq_prompt
from app.services.mcq.requests import validate_request
from app.services.mcq.schemas import MCQResponse
from app.services.mcq.validator import MCQValidationError


class MCQGenerationAgent(BaseAgent[MCQResponse]):
    def __init__(self, retrieve_context, generate_text, *, evaluator=None):
        self.retrieve_context = retrieve_context
        self.generate_text = generate_text
        self.evaluator = evaluator if evaluator is not None else EvaluationAgent(generate_text)


    def generate(self, document_id: str, scope=None, count: int = 5, *, previous_questions=()) -> MCQResponse:
        return self.run(document_id, scope=scope, count=count, previous_questions=previous_questions)


    def _run(self, document_id: str, scope=None, count: int = 5, *, previous_questions=()) -> MCQResponse:
        validate_request(document_id, scope, count)
        try:
            passages = retrieve_passages(self.retrieve_context, document_id, scope)
            if not passages:
                raise MCQGenerationError(
                    "No relevant document content with PDF page numbers was found for this section."
                )
            raw = self.generate_text(
                MCQ_SYSTEM_PROMPT,
                build_mcq_prompt(passages, scope, count, previous_questions),
            )
            check_active()
            return self.evaluator.evaluate(
                raw, passages, document_id=document_id, count=count,
                previous_questions=previous_questions,
            )
        except (TaskCancelled, TaskDeadline, MCQGenerationError):
            raise
        except MCQValidationError as error:
            raise MCQGenerationError(str(error)) from error
        except Exception as error:
            raise MCQGenerationError("The quiz service is temporarily unavailable.") from error
