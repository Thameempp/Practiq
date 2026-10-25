export function buildQuizVerification(question, scope = null) {
  const correct = question.options.find((option) => option.isCorrect)
  return {
    knowledge_base_id: question.sources[0]?.knowledge_base_id || 'local',
    target: {
      response_id: question.id,
      artifact: 'mcq',
      scope,
      question: question.question,
      answer: `Options: ${question.options.map((option) => `${option.key}: ${option.text}`).join('; ')}\nSelected answer: ${correct.key}: ${correct.text}\nExplanation: ${question.explanation}`,
      objection: 'Verify the selected answer and explanation against the PDF, including whether the options are unambiguous.',
      document_ids: [...new Set(question.sources.map((source) => source.document_id))],
      source_ids: [...new Set(question.sources.map((source) => source.citation_id).filter(Boolean))],
    },
  }
}
