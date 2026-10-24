import re

from app.documents.conversation import clear_state, read_state, write_state
from app.documents.matching import named_matches, ordinal_index
from app.query.schemas import QueryAnalysis
from app.query.analyzer import analyze_query


def pending_request(request, documents):
    pending = read_state(request.knowledge_base_id, request.conversation_id, "pending")
    if not pending:
        return None
    fresh = analyze_query(request.question, has_documents=bool(documents))
    if not request.selection_id and (fresh.intent.startswith("summarize") or fresh.intent == "create_study_material"
            or re.match(r"^(?:what|why|how|when|where|who|explain|compare|contrast|describe)\b", request.question, re.I)):
        return None
    by_id = {doc.document_id: doc for doc in documents}
    candidates = [by_id[value] for value in pending["candidate_document_ids"] if value in by_id]
    # Ordinals must retain their original positions, including a deleted slot.
    index = ordinal_index(request.question, pending=True)
    selection = request.selection_id
    if index is not None:
        ids = pending["candidate_document_ids"]
        selection = ids[index] if 0 <= index < len(ids) else "__missing__"
    matches = named_matches(request.question, candidates)
    if not selection and len(matches) == 1:
        selection = matches[0].document_id
    all_selection = bool(re.fullmatch(r"(?:all|all of them|both)(?: please)?[.!]?", request.question.strip(), re.I))
    if not selection and ".pdf" in request.question.casefold() and not matches:
        selection = "__missing__"
    if selection or all_selection or len(matches) > 1:
        analysis = QueryAnalysis.model_validate(pending["analysis"])
        if all_selection:
            analysis.document_scope = "all"
        elif not selection:
            analysis.document_reference = request.question
        return analysis, pending["question"], selection
    return None


def save_clarification(request, analysis, resolution, question=None):
    write_state(request.knowledge_base_id, request.conversation_id, "pending", {
        "question": question or request.question, "analysis": analysis.model_dump(),
        "candidate_document_ids": resolution.candidate_document_ids,
    })


def remember_selection(request, document_ids):
    clear_state(request.knowledge_base_id, request.conversation_id)
    write_state(request.knowledge_base_id, request.conversation_id, "context",
                {"document_ids": document_ids}, ttl=60 * 60)
