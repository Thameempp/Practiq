"""Reserve output and framing first; fit complete history pairs and PDF passages."""

from dataclasses import dataclass
import logging

from app.chat.prompts import user_prompt
from app.chat.tokens import clip_tokens, message_tokens, turn_messages
from app.core.config import settings
from app.orchestration.errors import TaskFailure
from app.services.retrieval.context import format_context
from app.services.retrieval.tokens import token_count_method

logger = logging.getLogger(__name__)


class PromptBudgetError(TaskFailure):
    pass


@dataclass
class PromptPlan:
    prompt: str
    history: list[dict]
    chunks: list[dict]
    input_tokens: int


def input_limit() -> int:
    return settings.CHAT_CONTEXT_TOKENS - settings.CHAT_OUTPUT_TOKENS - settings.CHAT_SAFETY_TOKENS


def fit_history(turns, limit):
    history = []
    for turn in reversed(turns):
        pair = turn_messages(turn)
        if not history and message_tokens(pair) > limit:
            question = clip_tokens(turn["question"], max(0, limit // 3 - 16))
            answer = clip_tokens(turn["answer"], max(0, limit - message_tokens([{"content": question}]) - 16))
            pair = [{"role": "user", "content": question}, {"role": "assistant", "content": answer}]
            if not question or not answer:
                break
        if message_tokens(pair + history) > limit:
            break
        history = pair + history
    return history


def build_prompt(system, question, chunks, *, scope_text="", turns=(), preamble=""):
    def messages(selected, history=()):
        prompt = user_prompt(question, format_context(selected), scope_text, preamble)
        return [{"role": "system", "content": system}, *history, {"role": "user", "content": prompt}]
    limit = input_limit()
    minimum = message_tokens(messages(chunks[:1]))
    if minimum > limit:
        raise PromptBudgetError("The question or selected section exceeds the chat token budget. Narrow your question or section.")
    history = fit_history(turns, min(settings.CHAT_HISTORY_TOKENS, limit - minimum))
    selected = []
    for chunk in chunks:
        if message_tokens(messages([*selected, chunk], history)) <= limit:
            selected.append(chunk)
    final = messages(selected, history)
    logger.info("Chat input_tokens=%s history_messages=%s evidence_chunks=%s output_limit=%s counter=%s",
                message_tokens(final), len(history), len(selected), settings.CHAT_OUTPUT_TOKENS, token_count_method())
    return PromptPlan(final[-1]["content"], history, selected, message_tokens(final))


def validate_messages(messages):
    if message_tokens(messages) > input_limit():
        raise PromptBudgetError("The chat request exceeds the configured token budget. Narrow your question or section.")
