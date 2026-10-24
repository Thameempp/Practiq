import time

from app.documents.database import connection
from app.documents.models import Document
from app.chat.store import forget_document
from app.services.verification.storage import forget_verification


def save_document(document: Document):
    with connection() as db:
        db.execute("""INSERT INTO documents VALUES (?, ?, ?, ?)
            ON CONFLICT(document_id) DO UPDATE SET payload=excluded.payload
            WHERE documents.knowledge_base_id=excluded.knowledge_base_id""",
            (document.document_id, document.knowledge_base_id, document.model_dump_json(), time.time()))


def list_documents(knowledge_base_id="local", order=()) -> list[Document]:
    with connection() as db:
        rows = db.execute("SELECT payload FROM documents WHERE knowledge_base_id=? ORDER BY created_at, document_id",
                          (knowledge_base_id,)).fetchall()
    documents = [Document.model_validate_json(row["payload"]) for row in rows]
    positions = {value: index for index, value in enumerate(dict.fromkeys(order))}
    return sorted(documents, key=lambda doc: positions.get(doc.document_id, len(positions)))


def get_document(document_id, knowledge_base_id="local") -> Document | None:
    with connection() as db:
        row = db.execute("SELECT payload FROM documents WHERE document_id=? AND knowledge_base_id=?",
                         (document_id, knowledge_base_id)).fetchone()
    return Document.model_validate_json(row["payload"]) if row else None


def delete_record(document_id, knowledge_base_id="local"):
    from app.services.understanding.storage import forget_map
    with connection() as db:
        deleted = db.execute("DELETE FROM documents WHERE document_id=? AND knowledge_base_id=?",
                             (document_id, knowledge_base_id)).rowcount
        if deleted:
            db.execute("DELETE FROM practice_questions WHERE document_id=?", (document_id,))
            forget_map(db, document_id, knowledge_base_id)
            forget_document(db, document_id, knowledge_base_id)
            forget_verification(db, document_id, knowledge_base_id)
            db.execute("DELETE FROM document_topics WHERE document_id=? AND knowledge_base_id=?",
                       (document_id, knowledge_base_id))
            db.execute("DELETE FROM summary_checkpoints WHERE document_id=?", (document_id,))
            db.execute("DELETE FROM citation_sources WHERE document_id=? AND knowledge_base_id=?",
                       (document_id, knowledge_base_id))
