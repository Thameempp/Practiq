import sqlite3
from contextlib import contextmanager

from app.core.config import settings
from app.services.understanding.schema import SCHEMA as MAP_SCHEMA

DB_PATH = settings.DATA_DIR / "knowledge_base.sqlite3"
SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY, knowledge_base_id TEXT NOT NULL,
    payload TEXT NOT NULL, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS conversation_state (
    knowledge_base_id TEXT NOT NULL, conversation_id TEXT NOT NULL,
    kind TEXT NOT NULL, payload TEXT NOT NULL, expires_at REAL NOT NULL,
    PRIMARY KEY (knowledge_base_id, conversation_id, kind)
);
CREATE TABLE IF NOT EXISTS summary_checkpoints (
    document_id TEXT NOT NULL, cache_key TEXT NOT NULL, summary TEXT NOT NULL,
    created_at REAL NOT NULL, PRIMARY KEY (document_id, cache_key)
);
CREATE TABLE IF NOT EXISTS citation_sources (
    id TEXT PRIMARY KEY, knowledge_base_id TEXT NOT NULL,
    document_id TEXT NOT NULL, payload TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS citation_documents ON citation_sources(document_id);
CREATE TABLE IF NOT EXISTS document_topics (
    document_id TEXT PRIMARY KEY, knowledge_base_id TEXT NOT NULL, payload TEXT NOT NULL
);
"""
SCHEMA += MAP_SCHEMA
SCHEMA += """
CREATE TABLE IF NOT EXISTS practice_questions (
    document_id TEXT NOT NULL, topic_key TEXT NOT NULL,
    question_key TEXT NOT NULL, question TEXT NOT NULL,
    PRIMARY KEY (document_id, topic_key, question_key)
);
"""


@contextmanager
def connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    try:
        db.executescript(SCHEMA)
        with db:
            yield db
    finally:
        db.close()
