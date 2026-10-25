export function buildQuestionRequest({ question, scope = null, conversationId, documents = [], selectionId = null, outline = [] }) {
  return {
    question,
    scope,
    document_id: scope?.documentId || null,
    knowledge_base_id: 'local',
    conversation_id: conversationId,
    document_order: documents.map((doc) => doc.documentId),
    selection_id: selectionId,
    outline,
  }
}
