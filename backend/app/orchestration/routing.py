from app.documents import repository
from app.chat.context import followup_documents
from app.documents.clarification import pending_request, remember_selection, save_clarification
from app.documents.conversation import clear_state, read_state
from app.documents.resolver import resolve_documents, resolve_qa, selected
from app.documents.sections import section_range
from app.documents.summary_scope import whole_document_summary
from app.orchestration.decision import RoutingDecision
from app.query.analyzer import analyze_query
from app.services.verification.routing import route_verification


def route_request(request):
    documents = repository.list_documents(request.knowledge_base_id, request.document_order)
    current_analysis = analyze_query(request.question, has_documents=bool(documents))
    if current_analysis.intent == "verify_answer":
        return route_verification(request, current_analysis, documents)
    resumed = pending_request(request, documents)
    analysis = resumed[0] if resumed else current_analysis
    question = resumed[1] if resumed else request.question
    selection_id = resumed[2] if resumed else request.selection_id
    scope = request.scope.model_dump() if request.scope else None
    context = read_state(request.knowledge_base_id, request.conversation_id, "context") or {}
    is_summary = analysis.intent.startswith("summarize")
    if request.selection_id and not resumed:
        return RoutingDecision("clarification_required", question, analysis, message="That selection has expired. Ask your question again.")
    if is_summary and scope and not analysis.document_reference and analysis.document_scope != "all":
        selection_id = selection_id or scope.get("documentId")
    if is_summary and not analysis.chapter_reference and whole_document_summary(question):
        scope = None
    if not is_summary and not resumed:
        clear_state(request.knowledge_base_id, request.conversation_id)
    if analysis.intent == "create_study_material":
        return RoutingDecision("unsupported_task", question, analysis, message="Study material is a separate task. Ask for a PDF summary or a specific question.")
    previous = followup_documents(request, documents) if not resumed else None
    if previous and analysis.intent in {"document_qa", "summarize_document"}:
        resolution = selected(previous)
    elif is_summary or resumed or analysis.intent == "cross_document_qa":
        resolution = resolve_documents(analysis, documents, message=request.question,
                                       context_ids=context.get("document_ids", []), selection_id=selection_id,
                                       pending=resumed is not None)
    else:
        resolution = resolve_qa(analysis, documents, request.question,
                                (scope or {}).get("documentId") or request.document_id)
    chosen = [doc for doc in documents if doc.document_id in resolution.document_ids]
    if resolution.status not in ("resolved", "all_documents"):
        if analysis.intent != "cross_document_qa" and resolution.status in ("clarification_required", "not_found"):
            save_clarification(request, analysis, resolution, question)
        choices = [doc for doc in documents if doc.document_id in resolution.candidate_document_ids]
        return RoutingDecision(resolution.status, question, analysis, choices, resolution.clarification_message)
    bounds = None
    if scope and (len(chosen) != 1 or scope.get("documentId") != chosen[0].document_id or analysis.document_reference):
        scope = None
    if is_summary and len(chosen) == 1 and (analysis.chapter_reference or scope):
        try:
            bounds = section_range(chosen[0], analysis.chapter_reference, scope)
        except ValueError as error:
            return RoutingDecision("clarification_required", question, analysis, message=str(error))
    remember_selection(request, resolution.document_ids)
    action = "summary" if is_summary else "cross_document_qa" if len(chosen) > 1 else "document_qa"
    if analysis.intent == "document_structure":
        action = "document_structure"
    return RoutingDecision(action, question, analysis, chosen, page_range=bounds, scope=scope,
                           knowledge_base_wide=not is_summary and resolution.status == "all_documents")
