from app.documents.repository import get_document
from app.citations.quiz import cite_quiz
from app.orchestration.decision import RoutingDecision
from app.orchestration.errors import TaskFailure
from app.query.schemas import QueryAnalysis
from app.services.mcq.generator import MCQGenerationError, generate_mcqs
from app.services.mcq.practice import generate_practice


def resolve_quiz(request):
    document = get_document(request.document_id, request.knowledge_base_id)
    if document is None:
        raise ValueError("PDF not found in this knowledge base.")
    if document.status != "ready":
        raise ValueError("Wait for PDF indexing to finish, or retry the failed upload.")
    if (request.scope or {}).get("documentId") not in (None, "", request.document_id):
        raise ValueError("The selected section belongs to a different document.")
    return RoutingDecision(
        "mcq",
        "Generate practice questions",
        QueryAnalysis(intent="document_qa"),
        [document],
        scope=request.scope,
    )


def generate_quiz_task(decision, context, count, exclude_questions=()):
    try:
        result = generate_practice(
            decision.documents[0].document_id, decision.scope, count,
            exclude_questions, generate_mcqs,
        )
    except MCQGenerationError as error:
        raise TaskFailure(str(error)) from error
    context.check()
    if not result.questions:
        raise TaskFailure("No practice questions were generated.")
    context.evidence.extend(
        source.model_dump()
        for question in result.questions
        for source in question.sources
    )
    return cite_quiz(result, decision.documents[0])
