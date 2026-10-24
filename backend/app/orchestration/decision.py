from dataclasses import dataclass, field

from app.documents.models import Document
from app.chat.models import ChatContext
from app.query.schemas import QueryAnalysis
from app.services.verification.models import VerificationTarget


@dataclass
class RoutingDecision:
    action: str
    question: str
    analysis: QueryAnalysis
    documents: list[Document] = field(default_factory=list)
    message: str | None = None
    page_range: tuple[int, int] | None = None
    scope: dict | None = None
    chat: ChatContext | None = None
    knowledge_base_wide: bool = False
    verification: VerificationTarget | None = None
    conversation_id: str | None = None


    def response(self):
        return {"status": self.action, "message": self.message,
                "documents": [{"document_id": doc.document_id, "filename": doc.filename,
                               "status": doc.status} for doc in self.documents]}
