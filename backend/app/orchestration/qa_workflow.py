from app.orchestration.runtime import check_active


def answer_question(decision):
    from app.services import generator
    query = decision.chat.query if decision.chat else decision.question
    chunks = generator.retrieve_context(query, scope=decision.scope,
                                        document_id=decision.documents[0].document_id)
    check_active()
    history = decision.chat.turns if decision.chat else ()
    yield from generator.answer_context(decision.question, chunks, decision.scope, turns=history,
                                        knowledge_base_id=decision.documents[0].knowledge_base_id)
