"""Include instructions and reserve completion tokens before splitting PDF text."""

from app.core.config import settings
from app.services.retrieval.tokens import count_tokens
from app.services.summary.models import SummaryChunk, SummaryError
from app.services.summary.prompts import SYSTEM_PROMPT, summary_prompt


def input_tokens(prompt: str) -> int:
    return count_tokens(SYSTEM_PROMPT) + count_tokens(prompt) + 32


def check_prompt(prompt, config):
    if len(prompt.encode()) > config.max_prompt_bytes or input_tokens(prompt) > config.max_input_tokens:
        raise SummaryError("The summary request exceeds its input budget. Use a smaller section or outline.")


def source_tokens(config, outline=None, request=""):
    empty = summary_prompt([SummaryChunk("", 1, 999999)], final=True, mapping=True,
                           outline=outline, request=request, max_chars=config.max_summary_chars)
    available = config.max_input_tokens - input_tokens(empty) - 128
    if available < 128:
        raise SummaryError("The selected summary instructions leave no room for PDF content.")
    return available


def provider_options(config):
    options = {"max_completion_tokens": config.max_output_tokens}
    if settings.SUMMARY_MODEL.startswith("openai/gpt-oss-"):
        options["reasoning_effort"] = "low"
        options["include_reasoning"] = False
    return options


def summary_timeout(document):
    return settings.SUMMARY_MAX_TIMEOUT_SECONDS


def can_finalize(chunks, config, outline, request):
    if len(chunks) != 1:
        return False
    prompt = summary_prompt(chunks, final=True, mapping=True, outline=outline,
                            request=request, max_chars=config.max_summary_chars)
    return len(prompt.encode()) <= config.max_prompt_bytes and input_tokens(prompt) <= config.max_input_tokens
