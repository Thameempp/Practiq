"""Bounded sequential retries for transient provider failures."""

import logging
import random
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from app.orchestration.errors import TaskCancelled, TaskDeadline
from app.orchestration.runtime import check_active, current_task, request_timeout
from app.services.summary.models import SummaryConfig, SummaryError, SummaryPublishedError, SummaryOutputError
from app.services.summary.failures import failure_message
from app.services.summary.budget import check_prompt
from app.orchestration.runtime import report_progress
from app.services.summary.output import compact_prompt

logger = logging.getLogger(__name__)


def call_with_retry(generate_text, prompt: str, config: SummaryConfig) -> str:
    check_prompt(prompt, config)
    for attempt in range(config.max_retries + 1):
        try:
            check_active()
            result = generate_text(prompt)
            if not isinstance(result, str) or not result.strip():
                raise SummaryError("The summary model returned an empty response.")
            if len(result.strip()) > config.max_summary_chars:
                prompt = compact_prompt(result.strip(), prompt, config)
                raise SummaryError("The summary model exceeded the requested output size.")
            return result.strip()
        except (TaskCancelled, TaskDeadline, SummaryPublishedError, SummaryOutputError):
            raise
        except Exception as error:
            status = getattr(error, "status_code", None)
            transient = (isinstance(error, (SummaryError, ConnectionError, TimeoutError))
                         or status in (408, 429) or isinstance(status, int) and status >= 500
                         or type(error).__name__ in ("APIConnectionError", "APITimeoutError"))
            if not transient or attempt == config.max_retries:
                logger.warning("Summary request failed status=%s cause=%s", status, type(error).__name__)
                raise SummaryError(failure_message(error)) from error
            retry_after = _retry_after(error)
            if retry_after is not None and retry_after > config.max_delay:
                raise SummaryError(failure_message(error)) from error
            delay = retry_after if retry_after is not None else min(
                config.max_delay, config.base_delay * 2 ** attempt + random.uniform(0, 0.5)
            )
            logger.warning("Retrying PDF summary request (%s/%s) in %.1fs", attempt + 1, config.max_retries, delay)
            report_progress({"stage": "waiting", "label": f"Waiting {delay:.0f}s for the summary provider to become available."})
            context = current_task.get()
            if context is None:
                time.sleep(delay)
            else:
                context.cancel.wait(min(delay, request_timeout(delay)))
                check_active()


def _retry_after(error) -> float | None:
    response = getattr(error, "response", None)
    headers = getattr(response, "headers", {}) or {}
    value = headers.get("retry-after") or headers.get("Retry-After")
    if value is None:
        return None
    try:
        return max(0, float(value))
    except (ValueError, TypeError):
        try:
            date = parsedate_to_datetime(value)
            return max(0, (date - datetime.now(timezone.utc)).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return None
