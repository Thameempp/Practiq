"""Adapt the application's existing Groq client; SDK retries are disabled here."""

from app.core.config import settings
from app.orchestration.runtime import check_active, request_timeout
from app.services.summary.models import SummaryConfig, SummaryError
from app.services.summary.budget import check_prompt, input_tokens, provider_options
from app.services.summary.prompts import SYSTEM_PROMPT
from app.services.summary.pacing import get_limiter
from app.services.summary.quota import usage_tokens


def make_generate_text(client, *, config=None):
    config = config or SummaryConfig()
    # The summary retry policy owns retries, including Retry-After handling.
    bounded_client = client.with_options(max_retries=0, timeout=request_timeout())
    limiter = get_limiter(client, config)


    def generate_text(prompt: str) -> str:
        check_active()
        check_prompt(prompt, config)
        reservation = limiter.reserve(input_tokens(prompt) + config.max_output_tokens)
        response = bounded_client.chat.completions.create(
            model=settings.SUMMARY_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            timeout=request_timeout(),
            **provider_options(config),
        )
        limiter.reconcile(reservation, usage_tokens(response))
        check_active()
        choice = response.choices[0]
        if choice.finish_reason == "length":
            raise SummaryError("The summary model reached its output limit.")
        return choice.message.content or ""

    return generate_text
