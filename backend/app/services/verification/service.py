import logging

from app.agents.answer_verifier_agent import AnswerVerifierAgent
from app.citations.store import save_sources
from app.citations.models import Source
from app.documents.repository import get_document
from app.orchestration.errors import TaskCancelled, TaskDeadline
from app.orchestration.runtime import check_active, report_progress
from app.services.verification.evidence import load_sources, pinpoint_sources
from app.services.verification.llm import make_generate_text
from app.services.verification.models import Claim, ClaimSet, VerificationError
from app.services.verification.results import insufficient, make_result
from app.services.verification.search import targeted_search
from app.services.verification.storage import record_audit
from app.services.retrieval.topics import canonical_scope

logger = logging.getLogger(__name__)


def verify_target(target, client, knowledge_base_id: str, conversation_id: str | None = None):
    for document_id in target.document_ids:
        document = get_document(document_id, knowledge_base_id)
        if document is None or document.status != "ready":
            raise VerificationError("A source PDF is unavailable or not ready. The answer could not be confirmed.")
    if target.scope and target.scope.get("documentId") not in (None, *target.document_ids):
        raise VerificationError("The verification section belongs to a different PDF.")
    if target.scope:
        document_id = target.scope.get("documentId") or (target.document_ids[0] if len(target.document_ids) == 1 else None)
        if document_id is None:
            raise VerificationError("Choose the PDF for the selected topic before verifying.")
        try:
            scope = canonical_scope(document_id, target.scope)
        except ValueError as error:
            raise VerificationError(str(error)) from error
        target = target.model_copy(update={"scope": scope, "document_ids": [document_id]})
    agent = AnswerVerifierAgent(make_generate_text(client),
        lambda value: load_sources(value, knowledge_base_id),
        lambda value, claims: targeted_search(value, claims, knowledge_base_id), on_progress=report_progress)
    try:
        result = agent.verify(target)
    except (TaskCancelled, TaskDeadline):
        raise
    except Exception as error:
        logger.warning("Answer verification unavailable (%s)", type(error).__name__)
        claims = ClaimSet(claims=[Claim(id="c1", text=target.answer[:1800])], complete=False)
        review = insufficient(claims.claims, "The review could not be completed reliably; the previous answer remains unconfirmed.")
        result = make_result(target, claims, review, review, [], [], 0)
        report_progress({"stage": "complete", "label": "Verification complete"})
    check_active()
    pinpoint_sources(result, knowledge_base_id)
    save_sources([Source.model_validate(source) for source in result.sources])
    record_audit(result, target, knowledge_base_id, conversation_id)
    return result
