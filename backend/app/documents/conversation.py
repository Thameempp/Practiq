import json
import time

from app.documents.database import connection

PENDING_TTL = 15 * 60


def read_state(knowledge_base_id, conversation_id, kind):
    if not conversation_id:
        return None
    with connection() as db:
        db.execute("DELETE FROM conversation_state WHERE expires_at<=?", (time.time(),))
        row = db.execute("SELECT payload FROM conversation_state WHERE knowledge_base_id=? AND conversation_id=? AND kind=?",
                         (knowledge_base_id, conversation_id, kind)).fetchone()
    return json.loads(row["payload"]) if row else None


def write_state(knowledge_base_id, conversation_id, kind, payload, ttl=PENDING_TTL):
    if not conversation_id:
        return
    with connection() as db:
        db.execute("INSERT OR REPLACE INTO conversation_state VALUES (?, ?, ?, ?, ?)",
                   (knowledge_base_id, conversation_id, kind, json.dumps(payload), time.time() + ttl))


def clear_state(knowledge_base_id, conversation_id, kind="pending"):
    with connection() as db:
        db.execute("DELETE FROM conversation_state WHERE knowledge_base_id=? AND conversation_id=? AND kind=?",
                   (knowledge_base_id, conversation_id, kind))
