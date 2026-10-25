import { API_URL } from './apiConfig.js'


function wait(delay, signal) {
  return new Promise((resolve, reject) => {
    const abort = () => {
      clearTimeout(timer)
      signal.removeEventListener('abort', abort)
      reject(new DOMException('Practice cancelled', 'AbortError'))
    }
    const timer = setTimeout(() => { signal.removeEventListener('abort', abort); resolve() }, delay)
    signal.addEventListener('abort', abort, { once: true })
    if (signal.aborted) abort()
  })
}


export async function requestPractice(documentId, scope, count, previous, signal) {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const response = await fetch(`${API_URL}/mcq`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, signal,
        body: JSON.stringify({ document_id: documentId, scope, count,
          exclude_questions: previous.slice(-100).map((question) => question.question) }),
      })
      const payload = await response.json().catch(() => ({}))
      if (!response.ok) {
        const error = new Error(payload.detail || 'Unable to generate practice questions.')
        error.retryable = [429, 503].includes(response.status) && !error.message.includes('distinct question')
        error.delay = Math.min(60000, Math.max(0, Number(response.headers.get('retry-after')) * 1000))
        throw error
      }
      if (!Array.isArray(payload.questions) || payload.questions.some((question) =>
        !question.id || typeof question.question !== 'string' || question.options?.length !== 4
          || !question.sources?.length)) throw new Error('The quiz service returned invalid questions.')
      return payload.questions
    } catch (error) {
      if (signal.aborted || attempt === 2 || !(error.retryable || error instanceof TypeError)) throw error
      await wait(error.delay || 2000 * 2 ** attempt, signal)
    }
  }
}
