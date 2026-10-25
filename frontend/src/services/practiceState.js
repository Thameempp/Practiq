export const PRACTICE_BUFFER = 5


export function questionKey(text) {
  return text.normalize('NFKC').toLowerCase().match(/[\p{L}\p{N}]+/gu)?.join(' ') || ''
}


export function appendQuestions(current, incoming) {
  if (!Array.isArray(incoming) || !incoming.length) throw new Error('No new questions were returned.')
  const known = new Set(current.map((question) => questionKey(question.question)))
  const ids = new Set(current.map((question) => question.id))
  const added = incoming.map((question) => {
    const key = questionKey(question.question)
    if (!key || known.has(key)) throw new Error('No new distinct question was found. Practice is paused.')
    known.add(key)
    const id = ids.has(question.id) ? crypto.randomUUID() : question.id
    ids.add(id)
    return { ...question, id }
  })
  return [...current, ...added]
}


export function practiceState(saved = {}) {
  const questions = saved.questions || []
  return { questions, answers: saved.answers || {}, index: saved.index || 0,
    status: questions.length ? 'ready' : 'loading', pending: false, error: '', backgroundError: '' }
}
