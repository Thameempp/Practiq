"""Stream final prose once; never retry a response whose text may be visible."""

from app.core.config import settings
from app.orchestration.runtime import check_active, request_timeout
from app.services.summary.models import SummaryConfig, SummaryError, SummaryPublishedError, SummaryOutputError
from app.services.summary.prompts import EMPTY_CONTENT, SYSTEM_PROMPT
from app.services.summary.budget import check_prompt, input_tokens, provider_options
from app.services.summary.retry import call_with_retry
from app.services.summary.failures import failure_message
from app.orchestration.errors import TaskCancelled, TaskDeadline
from app.services.summary.pacing import get_limiter
from app.services.summary.quota import usage_tokens


def make_stream_generate_text(client, emit, config: SummaryConfig):
    limiter = get_limiter(client, config)


    def generate(prompt: str) -> str:
        check_active()
        check_prompt(prompt, config)
        reservation = limiter.reserve(input_tokens(prompt) + config.max_output_tokens)
        bounded = client.with_options(max_retries=0, timeout=request_timeout())
        stream = bounded.chat.completions.create(
            model=settings.SUMMARY_MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}],
            temperature=0.2, stream=True, timeout=request_timeout(),
            extra_body={"stream_options": {"include_usage": True}}, **provider_options(config),
        )
        text, published = "", 0
        try:
            iterator = iter(stream)
            while True:
                check_active()
                chunk = next(iterator, None)
                if chunk is None:
                    break
                check_active()
                limiter.reconcile(reservation, usage_tokens(chunk))
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                if choice.finish_reason == "length":
                    raise SummaryOutputError("The summary model reached its output limit. Request a briefer summary.")
                delta = choice.delta.content or ""
                text += delta
                if len(text.strip()) > config.max_summary_chars:
                    raise SummaryOutputError("The summary model exceeded the requested output size.")
                # Do not leak the boilerplate-only sentinel, even when tokenized.
                if not text.strip() or not published and EMPTY_CONTENT.startswith(text.strip()):
                    continue
                if len(text) > published:
                    emit(text[published:])
                    published = len(text)
            check_active()
            if not text.strip():
                raise SummaryError("The summary model returned an empty response.")
            if text.strip() != EMPTY_CONTENT and len(text) > published:
                emit(text[published:])
            return text.strip()
        except (TaskCancelled, TaskDeadline):
            raise
        except Exception as error:
            if published:
                raise SummaryPublishedError(failure_message(error)) from error
            raise
        finally:
            stream.close()

    return lambda prompt: call_with_retry(generate, prompt, config)
