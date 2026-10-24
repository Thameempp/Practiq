"""Application adapter; the agent owns the quiz-generation workflow."""

from typing import Any

from groq import Groq

from app.agents.mcq_generation_agent import MCQGenerationAgent
from app.core.config import settings
from app.services.mcq.errors import MCQGenerationError  # Public compatibility import.
from app.services.mcq.llm import make_generate_text
from app.services.mcq.schemas import MCQResponse
from app.services.retrieval.service import retrieve_context

client = Groq(api_key=settings.GROQ_API_KEY)


def generate_mcqs(
    document_id: str,
    scope: dict[str, Any] | None = None,
    count: int = 5,
    *,
    previous_questions=(),
) -> MCQResponse:
    agent = MCQGenerationAgent(retrieve_context, make_generate_text(client))
    return agent.generate(document_id, scope=scope, count=count, previous_questions=previous_questions)
