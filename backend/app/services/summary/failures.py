"""Safe provider failure messages; no raw provider body or document text."""

from app.services.summary.models import SummaryError


def failure_message(error):
    status = getattr(error, "status_code", None)
    if status == 413:
        return "The summary request exceeds the provider's quota. Lower SUMMARY_INPUT_TOKENS and try again; saved sections will be reused."
    if status == 429:
        return "The summary provider's quota is exhausted. Try again later; saved sections will be reused."
    if status in (401, 403):
        return "The summary provider rejected access. Check the backend provider configuration."
    if isinstance(error, SummaryError):
        return str(error)
    return "The summary provider could not complete this request. Try again; saved sections will be reused."
