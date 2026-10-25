import { appendQuestions } from './practiceState.js'


export function practiceCacheKey(documentId, scope) {
  return `practiq_mcq_${documentId}_${encodeURIComponent(scope?.id || scope?.title || 'document')}_rolling_v3`
}


export function loadPractice(key) {
  try {
    const cached = JSON.parse(localStorage.getItem(key) || 'null')
    if (!cached) {
      const legacy = JSON.parse(localStorage.getItem(key.replace('_rolling_v3', '_sources_v2')) || 'null')
      return { excluded: Array.isArray(legacy) ? legacy.filter((q) => typeof q.question === 'string') : [] }
    }
    if (!Array.isArray(cached.questions) || !cached.questions.length) return {}
    if (cached.questions.some((question) => !question.id || !question.sources?.length || question.options?.length !== 4)) return {}
    const questions = appendQuestions([], cached.questions)
    const answers = Object.fromEntries(questions.filter((question) =>
      question.options.some((option) => option.key === cached.answers?.[question.id]))
      .map((question) => [question.id, cached.answers[question.id]]))
    const index = Number.isInteger(cached.index) ? Math.max(0, Math.min(cached.index, questions.length - 1)) : 0
    return { questions, answers, index }
  } catch { return {} }
}


export function savePractice(key, { questions, answers, index }) {
  if (!questions.length) return
  try { localStorage.setItem(key, JSON.stringify({ questions, answers, index })) } catch {
    // A full or unavailable cache must not interrupt practice.
  }
}
