import logging

from groq import Groq
from google.genai.errors import ServerError as GeminiServerError

from app.core.config import settings
from app.citations.catalog import attach_sources
from app.citations.markers import cited_answer
from app.orchestration.runtime import capture_evidence
from app.orchestration.agent_activity import agent_activity
from app.orchestration.errors import TaskCancelled, TaskDeadline
from app.chat.budget import build_prompt
from app.chat.llm import stream_answer
from app.chat.prompts import NOT_FOUND_MESSAGE, QA_SYSTEM_PROMPT
from app.services.context import normalize_question
from app.services.hierarchy import (
    build_scope_prompt,
    parse_scope,
)
from app.services.retrieval.service import retrieve_context
from app.services.retrieval.topics import canonical_scope


client = Groq(api_key=settings.GROQ_API_KEY)
logger = logging.getLogger(__name__)


def ask_pdf(
    user_question: str,
    scope=None,
    document_id: str | None = None,
    outline: list[str] | None = None,
):
    normalized_question, legacy_scope = normalize_question(user_question)
    parsed_scope = parse_scope(scope) or parse_scope(legacy_scope)
    try:
        chunks = retrieve_context(normalized_question, parsed_scope, document_id)
    except (TaskCancelled, TaskDeadline):
        raise
    except GeminiServerError as error:
        logger.warning("Embedding service unavailable (%s)", type(error).__name__)
        yield "⚠️ The embedding service is temporarily unavailable. Please try again in a few seconds."
        return
    except Exception as error:
        logger.warning("Context retrieval failed (%s)", type(error).__name__)
        yield "⚠️ Could not retrieve context. Please try again."
        return

    yield from answer_context(normalized_question, chunks, parsed_scope)


def answer_context(user_question, chunks, scope=None, *, turns=(), knowledge_base_id="local"):
    if not chunks:
        yield NOT_FOUND_MESSAGE
        return
    chunks = attach_sources(chunks, knowledge_base_id)
    if scope and chunks[0].get("metadata", {}).get("topic_path"):
        scope = canonical_scope(chunks[0]["metadata"]["document_id"], scope)
    plan = build_prompt(QA_SYSTEM_PROMPT, user_question.strip(), chunks,
                        scope_text=build_scope_prompt(parse_scope(scope)), turns=turns)
    capture_evidence(plan.chunks)
    stream = (_stream_answer(QA_SYSTEM_PROMPT, plan.prompt, history=plan.history) if plan.history
              else _stream_answer(QA_SYSTEM_PROMPT, plan.prompt))
    yield from cited_answer(stream, plan.chunks)


def _stream_answer(system_prompt: str, user_prompt: str, *, history=()):
    with agent_activity("Answer Generation"):
        yield from stream_answer(client, system_prompt, user_prompt, history=history)
