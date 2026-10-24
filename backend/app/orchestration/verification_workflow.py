from app.citations.catalog import emit_metadata
from app.citations.markers import cited_answer
from app.citations.models import Source
from app.orchestration.runtime import capture_evidence, report_progress
from app.services.verification.render import render_result
from app.services.verification.service import verify_target


def verify_answer(decision):
    from app.services.generator import client
    report_progress({"stage": "detecting", "label": "Understanding your concern…"})
    result = verify_target(decision.verification, client, decision.documents[0].knowledge_base_id,
                           decision.conversation_id)
    chunks = [{"text": source["quote"], "page_start": source["page"], "page_end": source["page_end"],
               "metadata": {"document_id": source["document_id"]}, "source": Source.model_validate(source)}
              for source in result.sources]
    capture_evidence(chunks)
    emit_metadata("verification", result.model_dump())
    yield from cited_answer(iter([render_result(result)]), chunks)
    return result.model_dump()
