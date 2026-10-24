import json
import re
import time

from app.core.config import settings
from app.chat.store import read_turns
from app.documents.conversation import read_state, write_state
from app.documents.database import connection
from app.services.verification.budget import bounded_target
from app.services.verification.models import VerificationTarget


def save_target(run, answer: str) -> None:
    chat = run.decision.chat
    if chat is None or run.decision.action == "verify_answer":
        return
    ids = re.findall(r"#source-(c[a-f0-9]{24})", answer)
    ids.extend(chunk["source"].id for task in run.state.tasks.values()
               for chunk in task.evidence if chunk.get("source"))
    target = VerificationTarget(response_id=run.state.request_id, question=run.decision.question,
        answer=answer[:40000], truncated=len(answer) > 40000, document_ids=list(chat.document_ids),
        source_ids=list(dict.fromkeys(ids))[:32], scope=run.decision.scope,
        artifact="summary" if run.decision.action == "summary" else "answer")
    payload = {**bounded_target(target).model_dump(), "knowledge_base_wide": chat.knowledge_base_wide}
    write_state(chat.knowledge_base_id, chat.conversation_id, "verification_target", payload,
                ttl=settings.CHAT_TTL_SECONDS)


def read_target(knowledge_base_id: str, conversation_id: str | None):
    saved = read_state(knowledge_base_id, conversation_id, "verification_target")
    if saved:
        return saved
    turns = read_turns(knowledge_base_id, conversation_id)
    if not turns:
        return None
    last = turns[-1]
    return {"response_id": last["request_id"], "question": last["question"], "answer": last["answer"],
            "document_ids": last["document_ids"], "truncated": True,
            "source_ids": list(dict.fromkeys(re.findall(r"#source-(c[a-f0-9]{24})", last["answer"])))[:32],
            "knowledge_base_wide": last.get("knowledge_base_wide", False)}


def record_audit(result, target, knowledge_base_id: str, conversation_id: str | None) -> None:
    if not conversation_id:
        return
    entry = {"response_id": result.response_id, "original_response_id": target.response_id,
             "document_ids": target.document_ids, "initial_verdict": result.initial_verdict,
             "scope": result.scope,
             "verdict": result.verdict, "evidence_ids": [source["id"] for source in result.sources],
             "reasons": [c.reason[:300] for c in result.claims],
             "corrected": bool(result.corrected_answer), "created_at": time.time()}
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT payload FROM conversation_state WHERE knowledge_base_id=? AND conversation_id=? AND kind='verification_audit' AND expires_at>?",
                         (knowledge_base_id, conversation_id, time.time())).fetchone()
        entries = [*(json.loads(row["payload"]) if row else []), entry][-10:]
        db.execute("INSERT OR REPLACE INTO conversation_state VALUES (?, ?, 'verification_audit', ?, ?)",
                   (knowledge_base_id, conversation_id, json.dumps(entries), time.time() + settings.CHAT_TTL_SECONDS))


def forget_verification(db, document_id: str, knowledge_base_id: str) -> None:
    rows = db.execute("SELECT conversation_id, kind, payload FROM conversation_state WHERE knowledge_base_id=? AND kind IN ('verification_target', 'verification_audit')",
                      (knowledge_base_id,)).fetchall()
    for row in rows:
        value = json.loads(row["payload"])
        if row["kind"] == "verification_audit":
            value = [entry for entry in value if document_id not in entry["document_ids"]]
        elif document_id not in value["document_ids"]:
            continue
        else:
            value = None
        if value:
            db.execute("UPDATE conversation_state SET payload=? WHERE knowledge_base_id=? AND conversation_id=? AND kind=?",
                       (json.dumps(value), knowledge_base_id, row["conversation_id"], row["kind"]))
        else:
            db.execute("DELETE FROM conversation_state WHERE knowledge_base_id=? AND conversation_id=? AND kind=?",
                       (knowledge_base_id, row["conversation_id"], row["kind"]))
