from dataclasses import dataclass
from app.core.config import settings
from app.orchestration.errors import TaskFailure


class SummaryError(TaskFailure):
    """The complete document could not be summarized safely."""


class SummaryPublishedError(SummaryError):
    """A final response failed after publishing text and must never be replayed."""


class SummaryOutputError(SummaryError):
    """A final output exceeded a fixed limit; repeating the same request is unsafe."""


@dataclass(frozen=True)
class SummaryChunk:
    text: str
    page_start: int
    page_end: int


@dataclass(frozen=True)
class SummaryConfig:
    max_retries: int = 3
    max_summaries_per_group: int = 4
    max_chunk_chars: int = 20_000
    max_prompt_bytes: int = 64_000
    max_summary_chars: int = 6000
    intermediate_chars: int = 1200
    max_input_tokens: int = settings.SUMMARY_INPUT_TOKENS
    max_output_tokens: int = settings.SUMMARY_OUTPUT_TOKENS
    base_delay: float = 1.0
    max_delay: float = 120.0
    requests_per_minute: int = settings.SUMMARY_REQUESTS_PER_MINUTE
    tokens_per_minute: int = settings.SUMMARY_TOKENS_PER_MINUTE
    digest_threshold_pages: int = settings.SUMMARY_DIGEST_THRESHOLD_PAGES
    page_digest_chars: int = settings.SUMMARY_PAGE_DIGEST_CHARS


    def __post_init__(self):
        object.__setattr__(self, "max_input_tokens", min(self.max_input_tokens,
                           self.tokens_per_minute - self.max_output_tokens))
        if self.max_retries < 0 or self.max_summaries_per_group < 2:
            raise ValueError("Retries must be nonnegative and merge groups must contain at least 2 items.")
        if self.max_chunk_chars < 1 or self.max_prompt_bytes < 4096:
            raise ValueError("Chunk size must be positive and prompt budget at least 4096 bytes.")
        if self.max_summary_chars < 1 or not 0 <= self.base_delay <= self.max_delay:
            raise ValueError("Summary size and retry delays are invalid.")
        if self.max_input_tokens < 2048 or self.max_output_tokens < 128 or self.intermediate_chars < 1:
            raise ValueError("Summary token and intermediate limits are invalid.")
        if self.requests_per_minute < 1 or self.tokens_per_minute < 1:
            raise ValueError("Summary provider rates must be positive.")
        if self.digest_threshold_pages < 1 or self.page_digest_chars < 300:
            raise ValueError("Summary page-digest limits are invalid.")
