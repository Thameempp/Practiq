"""Persist per-document/topic question history; commit novelty checks atomically."""

import hashlib
import json
import sqlite3
from collections.abc import Sequence

from app.documents.database import connection
from app.services.mcq.errors import MCQGenerationError
from app.services.mcq.novelty import ensure_distinct, normalized_question

def topic_key(scope: dict | None) -> str:
    scope = scope or {}
    value = scope.get("id") or [scope.get("title", "document"), scope.get("page")]
    return hashlib.sha256(json.dumps(value, ensure_ascii=False).encode()).hexdigest()


def _read(db: sqlite3.Connection, document_id: str, key: str) -> list[str]:
    return [row[0] for row in db.execute(
        "SELECT question FROM practice_questions WHERE document_id=? AND topic_key=? ORDER BY rowid",
        (document_id, key),
    )]


def load_history(document_id: str, scope: dict | None) -> list[str]:
    with connection() as db:
        return _read(db, document_id, topic_key(scope))


def save_questions(
    document_id: str,
    scope: dict | None,
    questions: list[str],
    excluded: Sequence[str] = (),
) -> None:
    key = topic_key(scope)
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        if not db.execute("SELECT 1 FROM documents WHERE document_id=?", (document_id,)).fetchone():
            raise MCQGenerationError("The PDF is no longer available.")
        ensure_distinct(questions, _read(db, document_id, key) + list(excluded))
        db.executemany("INSERT OR IGNORE INTO practice_questions VALUES (?, ?, ?, ?)", [
            (document_id, key, normalized_question(text), text)
            for text in [*excluded, *questions]
        ])
