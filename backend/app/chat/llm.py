"""Bounded QA generation; history is context and current PDF passages are evidence."""

import logging

from app.chat.budget import PromptBudgetError, validate_messages
from app.core.config import settings
from app.orchestration.runtime import check_active, current_task, request_timeout

logger = logging.getLogger(__name__)


def stream_answer(client, system_prompt, user_prompt, *, history=()):
    messages = [{"role": "system", "content": system_prompt}, *history,
                {"role": "user", "content": user_prompt}]
    validate_messages(messages)
    stream = None
    try:
        check_active()
        active = client.with_options(max_retries=0, timeout=request_timeout()) if current_task.get() else client
        response = active.chat.completions.with_raw_response.create(
            messages=messages, model=settings.LLM_MODEL, stream=True,
            max_completion_tokens=settings.CHAT_OUTPUT_TOKENS, timeout=request_timeout(),
            extra_body={"stream_options": {"include_usage": True}},
        )
        stream, received = response.parse(), False
        iterator = iter(stream)
        while True:
            check_active()
            chunk = next(iterator, None)
            if chunk is None:
                break
            check_active()
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            if getattr(choice, "finish_reason", None) == "length":
                raise PromptBudgetError(
                    "The answer reached its output token limit. Ask for a shorter answer or a narrower topic."
                )
            content = choice.delta.content
            if content:
                received = True
                yield content
        check_active()
        if not received:
            raise RuntimeError("The answer model returned no content.")
    except Exception as error:
        if current_task.get() is not None:
            raise
        logger.warning("Answer generation failed (%s)", type(error).__name__)
        yield "The answer could not be completed. Please try again."
    finally:
        close = getattr(stream, "close", None)
        if callable(close):
            close()
