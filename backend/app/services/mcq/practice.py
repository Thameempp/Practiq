"""Bound fresh-question attempts without returning duplicates or skipping evaluation."""

from uuid import uuid4
from collections.abc import Callable, Sequence

from app.orchestration.runtime import check_active
from app.services.mcq.history import load_history, save_questions
from app.services.mcq.novelty import DuplicateQuestion, ensure_distinct
from app.services.mcq.schemas import MCQResponse


def generate_practice(
    document_id: str,
    scope: dict | None,
    count: int,
    excluded: Sequence[str],
    generate: Callable[..., MCQResponse],
) -> MCQResponse:
    previous = list(dict.fromkeys([*load_history(document_id, scope), *excluded]))
    for attempt in range(2):
        check_active()
        try:
            result = generate(document_id, scope=scope, count=count, previous_questions=previous)
            texts = [question.question for question in result.questions]
            check_active()
            ensure_distinct(texts, previous)
            save_questions(document_id, scope, texts, excluded)
        except DuplicateQuestion as error:
            if attempt == 1:
                raise
            previous.extend(error.questions)
            continue
        return MCQResponse(questions=[
            question.model_copy(update={"id": uuid4().hex}) for question in result.questions
        ])
