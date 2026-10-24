from app.documents.matching import named_matches, ordinal_index
from app.documents.models import DocumentResolution
from app.query.patterns import CONTEXTUAL, GENERIC


def resolve_documents(analysis, documents, *, message="", context_ids=(), selection_id=None, pending=False):
    available = {doc.document_id: doc for doc in documents}
    if not documents:
        return _result("no_documents", "Upload a PDF to your knowledge base first.")
    if selection_id:
        if selection_id not in available:
            return _result("not_found", "That PDF is not available in this knowledge base.", documents)
        return selected([available[selection_id]])
    if analysis.document_scope == "all":
        return selected(documents, all_documents=True)
    reference = analysis.document_reference or ""
    matches = named_matches(reference, documents)
    if matches:
        return selected(matches) if len(matches) == 1 else _result("clarification_required", "Which PDF would you like me to summarize?", matches)
    ordinal = ordinal_index(message, pending=pending)
    if ordinal is not None:
        return selected([documents[ordinal]]) if 0 <= ordinal < len(documents) else _result("not_found", "That PDF number is not in this list.", documents)
    if CONTEXTUAL.search(message) and context_ids:
        matches = [available[value] for value in context_ids if value in available]
        if len(matches) == 1:
            return selected(matches)
    if reference and not GENERIC.fullmatch(reference) and not CONTEXTUAL.fullmatch(reference):
        return _result("not_found", "I could not find that PDF. Choose one of the available files.", documents)
    if len(documents) == 1:
        return selected(documents)
    return _result("clarification_required", "Which PDF would you like me to summarize?", documents)


def selected(documents, all_documents=False):
    waiting = [doc.filename for doc in documents if doc.status != "ready"]
    if waiting:
        return _result("processing", "These PDFs are not ready: " + ", ".join(waiting) + ". Wait for indexing or retry a failed upload.", documents)
    return DocumentResolution(status="all_documents" if all_documents else "resolved",
                              document_ids=[doc.document_id for doc in documents])


def _result(status, message, documents=()):
    return DocumentResolution(status=status, clarification_message=message,
                              candidate_document_ids=[doc.document_id for doc in documents])


def resolve_qa(analysis, documents, message, active_id=None):
    if not documents:
        return _result("no_documents", "Upload a PDF to your knowledge base first.")
    if analysis.document_scope == "all":
        return selected(documents, all_documents=True)
    named = named_matches(message, documents)
    if named:
        return selected(named)
    if ".pdf" in message.casefold():
        return _result("not_found", "I could not find that PDF in this knowledge base.", documents)
    if active_id:
        matched = [doc for doc in documents if doc.document_id == active_id]
        return selected(matched) if matched else _result("not_found", "That PDF is not available in this knowledge base.")
    return selected(documents, all_documents=True)
