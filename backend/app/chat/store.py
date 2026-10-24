"""Atomic, bounded transcript storage in the existing SQLite state table."""

import json
import time

from app.chat.retention import retain_turns
from app.core.config import settings
from app.documents.conversation import read_state
from app.documents.database import connection


def read_turns(knowledge_base_id, conversation_id) -> list[dict]:
    return read_state(knowledge_base_id, conversation_id, "history") or []


def append_turn(knowledge_base_id, conversation_id, turn):
    if not conversation_id:
        return
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        db.execute("DELETE FROM conversation_state WHERE expires_at<=?", (time.time(),))
        row = db.execute("SELECT payload FROM conversation_state WHERE knowledge_base_id=? AND conversation_id=? AND kind='history'",
                         (knowledge_base_id, conversation_id)).fetchone()
        turns = json.loads(row["payload"]) if row else []
        payload = json.dumps(retain_turns([*turns, turn]), ensure_ascii=False)
        db.execute("INSERT OR REPLACE INTO conversation_state VALUES (?, ?, 'history', ?, ?)",
                   (knowledge_base_id, conversation_id, payload, time.time() + settings.CHAT_TTL_SECONDS))


def forget_document(db, document_id, knowledge_base_id):
    rows = db.execute("SELECT conversation_id, payload FROM conversation_state WHERE knowledge_base_id=? AND kind='history'",
                      (knowledge_base_id,)).fetchall()
    for row in rows:
        turns = [turn for turn in json.loads(row["payload"]) if document_id not in turn["document_ids"]]
        db.execute("UPDATE conversation_state SET payload=? WHERE knowledge_base_id=? AND conversation_id=? AND kind='history'",
                   (json.dumps(turns, ensure_ascii=False), knowledge_base_id, row["conversation_id"]))
