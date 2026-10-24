"""Use a configured local generation tokenizer, with a conservative offline fallback."""

import logging
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _tokenizer():
    if not settings.GENERATION_TOKENIZER_PATH:
        logger.info("Retrieval uses UTF-8 byte counts as a conservative token upper bound.")
        return None
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(settings.GENERATION_TOKENIZER_PATH, local_files_only=True)


def count_tokens(text: str) -> int:
    tokenizer = _tokenizer()
    return len(tokenizer.encode(text, add_special_tokens=False)) if tokenizer else len(text.encode("utf-8"))


def token_count_method() -> str:
    return "generation_tokenizer" if _tokenizer() is not None else "utf8_upper_bound"
