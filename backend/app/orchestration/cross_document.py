from app.orchestration.runtime import capture_evidence, check_active
from app.chat.budget import PromptBudgetError, build_prompt
from app.chat.prompts import NOT_FOUND_MESSAGE
from app.citations.catalog import attach_sources
from app.citations.markers import cited_answer
from app.query.patterns import COMPARISON
from app.services.retrieval.context import select_context
from app.services.retrieval.models import RetrievalConfig
from app.services.retrieval.service import retrieve_context
from app.services.retrieval.tokens import count_tokens


def answer_across_documents(decision):
    from app.services.generator import QA_SYSTEM_PROMPT, _stream_answer
    groups = []
    query = decision.chat.query if decision.chat else decision.question
    for doc in decision.documents:
        check_active()
        groups.append(retrieve_context(query, document_id=doc.document_id))
    missing = [doc.filename for doc, chunks in zip(decision.documents, groups) if not chunks]
    comparison = decision.analysis.intent == "cross_document_qa" or COMPARISON.search(decision.question)
    if missing and comparison:
        yield "I could not find evidence in: " + ", ".join(missing) + ". Narrow the question or select fewer PDFs."
        return
    groups = [group for group in groups if group]
    if not groups:
        yield NOT_FOUND_MESSAGE
        return
    # Give each requested PDF one opportunity before adding supplementary evidence.
    candidates = [group[0] for group in groups]
    candidates.extend(sorted([chunk for group in groups for chunk in group[1:]],
                             key=lambda chunk: chunk["rerank_score"], reverse=True))
    selected = select_context(candidates, count_tokens, RetrievalConfig(
        final_top_k=max(6, len(groups)), diversity_weight=0))
    represented = {chunk["metadata"]["document_id"] for chunk in selected}
    if any(group[0]["metadata"]["document_id"] not in represented for group in groups):
        yield "The evidence from all requested PDFs does not fit the context budget. Select fewer PDFs."
        return
    selected = attach_sources(selected, decision.documents[0].knowledge_base_id)
    plan = build_prompt(QA_SYSTEM_PROMPT, decision.question, selected,
                        turns=decision.chat.turns if decision.chat else (),
                        preamble="Answer from relevant evidence across the supplied PDFs; cite source_id markers. "
                                 "Do not assume every PDF covers the question. Distinguish conflicting sources.")
    if {chunk["metadata"]["document_id"] for chunk in plan.chunks} != represented:
        raise PromptBudgetError("The comparison exceeds the chat token budget. Select fewer PDFs.")
    capture_evidence(plan.chunks)
    stream = (_stream_answer(QA_SYSTEM_PROMPT, plan.prompt, history=plan.history) if plan.history
              else _stream_answer(QA_SYSTEM_PROMPT, plan.prompt))
    yield from cited_answer(stream, plan.chunks)
