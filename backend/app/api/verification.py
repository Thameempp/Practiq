from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.api.workflow_stream import response_headers, stream_workflow
from app.documents.repository import get_document
from app.orchestration.decision import RoutingDecision
from app.orchestration.service import get_orchestrator
from app.query.schemas import QueryAnalysis
from app.services.verification.models import VerificationTarget

router = APIRouter()


class VerificationRequest(BaseModel):
    target: VerificationTarget
    knowledge_base_id: str = Field(default="local", min_length=1, max_length=100)
    conversation_id: str | None = Field(default=None, min_length=1, max_length=100)


@router.post("/verify")
def verify(request: VerificationRequest, connection: Request):
    documents = [get_document(document_id, request.knowledge_base_id)
                 for document_id in dict.fromkeys(request.target.document_ids)]
    if any(document is None or document.status != "ready" for document in documents):
        raise HTTPException(422, "Every requested PDF must be available and ready in this knowledge base.")
    if request.target.scope and request.target.scope.get("documentId") not in (None, *request.target.document_ids):
        raise HTTPException(422, "The verification section belongs to a different PDF.")
    target = request.target.model_copy(update={"response_id": request.target.response_id or uuid4().hex})
    decision = RoutingDecision("verify_answer", target.objection or "Verify this answer",
        QueryAnalysis(intent="verify_answer"), documents, verification=target,
        conversation_id=request.conversation_id)
    coordinator = get_orchestrator()
    run = coordinator.from_decision(decision)
    if "text/event-stream" in connection.headers.get("accept", ""):
        return StreamingResponse(stream_workflow(coordinator, run, connection, sse=True),
                                 media_type="text/event-stream", headers=response_headers(run))
    list(coordinator.events(run))
    task = run.state.tasks["verify_answer"]
    if run.state.status != "succeeded":
        raise HTTPException(503, task.error or "The answer could not be verified.")
    return {**task.result, "content": task.text}
