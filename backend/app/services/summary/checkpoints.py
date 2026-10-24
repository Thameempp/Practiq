"""Reuse successful stages after quota waits/failures; never cache partial output."""

import hashlib
import json
import time
import logging
import sqlite3
from dataclasses import asdict

from app.core.config import settings
from app.documents.database import connection
from app.orchestration.runtime import check_active
from app.services.summary.models import SummaryError
from app.services.summary.prompts import EMPTY_CONTENT, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def cached_generate(document_id, generate, config, *, final=False, emit=None, revision=""):
    options = json.dumps({"model": settings.SUMMARY_MODEL, "config": {k: v for k, v in asdict(config).items()
                          if k not in ("requests_per_minute", "tokens_per_minute")},
                          "system": SYSTEM_PROMPT, "final": final, "revision": revision, "version": 3}, sort_keys=True)
    limit = config.max_summary_chars if final else config.intermediate_chars


    def run(prompt):
        check_active()
        key = hashlib.sha256((options + prompt).encode()).hexdigest()
        try:
            with connection() as db:
                row = db.execute("SELECT summary FROM summary_checkpoints WHERE document_id=? AND cache_key=? AND created_at>?",
                                 (document_id, key, time.time() - 7 * 86400)).fetchone()
        except sqlite3.Error:
            logger.warning("Summary checkpoint lookup unavailable")
            row = None
        if row:
            if emit and row["summary"] != EMPTY_CONTENT:
                emit(row["summary"])
            return row["summary"]
        text = generate(prompt)
        check_active()
        if not isinstance(text, str) or not text.strip() or len(text.strip()) > limit:
            raise SummaryError("The summary model returned an empty or oversized response.")
        try:
            with connection() as db:
                db.execute("DELETE FROM summary_checkpoints WHERE created_at<?", (time.time() - 7 * 86400,))
                db.execute("INSERT OR REPLACE INTO summary_checkpoints VALUES (?, ?, ?, ?)",
                           (document_id, key, text.strip(), time.time()))
        except sqlite3.Error:
            logger.warning("Summary checkpoint save unavailable")
        return text.strip()

    return run
