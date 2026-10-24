import json

from app.documents.database import connection
from app.services.understanding.models import DocumentMap

TABLES = ("document_maps", "document_map_pages", "document_map_sections", "document_map_topics")


def forget_map(db, document_id: str, knowledge_base_id: str) -> None:
    for table in TABLES:
        db.execute(f"DELETE FROM {table} WHERE document_id=? AND knowledge_base_id=?", (document_id, knowledge_base_id))


def save_map(document_map: DocumentMap) -> None:
    ids = (document_map.document_id, document_map.knowledge_base_id)
    with connection() as db:
        if not db.execute("SELECT 1 FROM documents WHERE document_id=? AND knowledge_base_id=?", ids).fetchone():
            raise ValueError("This PDF is no longer in the knowledge base.")
        forget_map(db, *ids)
        db.execute("INSERT INTO document_maps VALUES (?, ?, ?)",
                   (*ids, document_map.model_dump_json(exclude={"pages", "sections", "topics"})))
        db.executemany("INSERT INTO document_map_pages VALUES (?, ?, ?, ?)",
                       [(*ids, p.pdf_page, p.model_dump_json()) for p in document_map.pages])
        db.executemany("INSERT INTO document_map_sections VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       [(*ids, s.section_id, s.parent_section_id, s.section_type, s.start_page,
                         s.end_page, s.status, s.model_dump_json()) for s in document_map.sections])
        db.executemany("INSERT INTO document_map_topics VALUES (?, ?, ?, ?, ?, ?)",
                       [(*ids, t.topic_id, t.section_id, t.chapter_id, t.model_dump_json()) for t in document_map.topics])


def read_map(document_id: str, knowledge_base_id: str) -> DocumentMap | None:
    ids = (document_id, knowledge_base_id)
    with connection() as db:
        row = db.execute("SELECT payload FROM document_maps WHERE document_id=? AND knowledge_base_id=?", ids).fetchone()
        if row is None:
            return None
        payload = json.loads(row["payload"])
        for key, table, order in (("pages", "document_map_pages", "pdf_page"),
                                  ("sections", "document_map_sections", "COALESCE(start_page, 2147483647), rowid"),
                                  ("topics", "document_map_topics", "rowid")):
            rows = db.execute(f"SELECT payload FROM {table} WHERE document_id=? AND knowledge_base_id=? ORDER BY {order}", ids)
            payload[key] = [json.loads(item["payload"]) for item in rows]
    return DocumentMap.model_validate(payload)
