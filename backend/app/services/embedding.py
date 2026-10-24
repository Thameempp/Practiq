import logging
import time
from google import genai
from google.genai.errors import ServerError
from app.core.config import settings
from app.orchestration.runtime import check_active, current_task, request_timeout

client = genai.Client(api_key=settings.GOOGLE_API_KEY)
logger = logging.getLogger(__name__)

_MAX_RETRIES = 4
_BASE_DELAY  = 1.5   # seconds


def _with_retry(fn, *args, **kwargs):
    """
    Call fn(*args, **kwargs) with exponential backoff on 5xx / 503 errors.
    Raises the last exception if all retries are exhausted.
    """
    delay = _BASE_DELAY
    for attempt in range(_MAX_RETRIES):
        try:
            check_active()
            result = fn(*args, **kwargs)
            check_active()
            return result
        except ServerError as error:
            if attempt == _MAX_RETRIES - 1:
                raise
            logger.warning("Embedding transient failure (%s); retrying in %.1fs", type(error).__name__, delay)
            context = current_task.get()
            if context is None:
                time.sleep(delay)
            else:
                context.cancel.wait(request_timeout(delay))
                check_active()
            delay *= 2   # exponential back-off


def get_embedding(text: str) -> list[float]:
    def _call():
        result = client.models.embed_content(
            model=settings.EMBEDDING_MODEL,
            contents=text,
        )
        return result.embeddings[0].values
    return _with_retry(_call)


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Embed multiple texts in a single API call instead of one call per text."""


    def _call():
        result = client.models.embed_content(
            model=settings.EMBEDDING_MODEL,
            contents=texts,
        )
        return [e.values for e in result.embeddings]
    return _with_retry(_call)
