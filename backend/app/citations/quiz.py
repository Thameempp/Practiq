from app.citations.store import save_sources, source_for
from app.documents.models import Document
from app.services.mcq.schemas import MCQResponse


def cite_quiz(result: MCQResponse, document: Document) -> MCQResponse:
    sources = []
    for question in result.questions:
        for source in question.sources:
            if source.document_id != document.document_id or not 1 <= source.page <= document.pages:
                raise ValueError("The quiz source does not belong to this PDF.")
            record = source_for(document, source.page, source.quote)
            source.citation_id = record.id
            source.knowledge_base_id = document.knowledge_base_id
            source.filename = document.filename
            sources.append(record)
    save_sources(sources)
    return result
