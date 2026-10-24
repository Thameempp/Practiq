import json
import re
from hashlib import sha256

from app.chat.followup import contextual_query, is_followup
from app.chat.models import ChatContext
from app.chat.store import read_turns
from app.documents.matching import named_matches
from app.query.patterns import ALL_DOCUMENTS

CONTEXTUAL_DOCUMENT = re.compile(r"\b(?:that|previous)\s+(?:pdf|document|file)\b", re.I)


def scope_key(scope) -> str:
    if not scope:
        return "document"
    value = json.dumps({key: scope.get(key) for key in ("id", "title", "page", "documentId")}, sort_keys=True)
    return "section:" + sha256(value.encode()).hexdigest()


def attach_history(decision, request):
    if not request.conversation_id or decision.action not in {"document_qa", "cross_document_qa", "summary", "verify_answer", "document_structure"}:
        return decision
    ids = tuple(sorted(doc.document_id for doc in decision.documents))
    key = scope_key(decision.scope)
    turns = []
    for turn in reversed(read_turns(request.knowledge_base_id, request.conversation_id)):
        same_documents = tuple(turn["document_ids"]) == ids
        expanded = (decision.knowledge_base_wide and turn.get("knowledge_base_wide", False)
                    and set(turn["document_ids"]).issubset(ids))
        if not (same_documents or expanded) or turn["scope_key"] != key:
            break  # Switching PDFs/sections starts a fresh contextual segment.
        turns.append(turn)
    turns.reverse()
    question = decision.verification.question if decision.verification else decision.question
    query, topic = contextual_query(question, turns)
    decision.chat = ChatContext(request.knowledge_base_id, request.conversation_id,
                                ids, key, tuple(turns), query, topic,
                                knowledge_base_wide=decision.knowledge_base_wide)
    return decision


def followup_documents(request, documents):
    if request.scope or not request.conversation_id or not is_followup(request.question):
        return None
    if (ALL_DOCUMENTS.search(request.question) or ".pdf" in request.question.casefold()
            or named_matches(request.question, documents)):
        return None
    turns = read_turns(request.knowledge_base_id, request.conversation_id)
    if not turns or turns[-1]["scope_key"] != "document":
        return None
    # Global chat follows the current uploads, including files added after the last turn.
    global_chat = turns[-1].get("knowledge_base_wide", request.document_id is None)
    if global_chat and not CONTEXTUAL_DOCUMENT.search(request.question):
        return None
    ids = turns[-1]["document_ids"]
    if request.document_id and request.document_id not in ids:
        return None
    chosen = [doc for doc in documents if doc.document_id in ids]
    return chosen if len(chosen) == len(ids) else None
