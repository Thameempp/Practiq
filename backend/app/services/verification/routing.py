from app.documents.resolver import selected
from app.orchestration.decision import RoutingDecision
from app.services.verification.models import VerificationTarget
from app.services.verification.storage import read_target


def route_verification(request, analysis, documents):
    saved = read_target(request.knowledge_base_id, request.conversation_id)
    if not saved:
        return RoutingDecision("clarification_required", request.question, analysis,
            message="There is no previous answer to recheck in this chat. Ask a PDF question first, or provide an answer to /verify.")
    data = {key: value for key, value in saved.items() if key in VerificationTarget.model_fields}
    target = VerificationTarget.model_validate({**data, "objection": request.question})
    if request.document_id and request.document_id not in target.document_ids:
        return RoutingDecision("clarification_required", request.question, analysis,
                               message="The previous answer used a different PDF. Choose that answer's PDF before rechecking it.")
    if request.scope and request.scope.model_dump() != target.scope:
        return RoutingDecision("clarification_required", request.question, analysis,
                               message="The selected section differs from the previous answer. Clear the section selection to recheck it.")
    ids = {doc.document_id for doc in documents}
    if not set(target.document_ids).issubset(ids):
        return RoutingDecision("not_found", request.question, analysis,
                               message="A PDF used by the previous answer is no longer available.")
    if saved.get("knowledge_base_wide"):
        target = target.model_copy(update={"document_ids": [doc.document_id for doc in documents]})
    chosen = [doc for doc in documents if doc.document_id in target.document_ids]
    resolution = selected(chosen)
    if resolution.status == "processing":
        return RoutingDecision("processing", request.question, analysis, chosen, resolution.clarification_message)
    return RoutingDecision("verify_answer", request.question, analysis, chosen, verification=target,
                           conversation_id=request.conversation_id, scope=target.scope,
                           knowledge_base_wide=bool(saved.get("knowledge_base_wide")))
