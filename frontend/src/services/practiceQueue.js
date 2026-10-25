import { appendQuestions, PRACTICE_BUFFER, practiceState } from './practiceState.js'


export function createPracticeQueue(saved, request, publish) {
  let state = practiceState(saved)
  let disposed = false
  let busy = false


  function update(patch) {
    state = { ...state, ...patch }
    publish(state)
  }


  async function refill() {
    if (disposed || busy) return
    busy = true
    update({ pending: true, error: '', backgroundError: '' })
    try {
      while (!disposed && state.questions.length < PRACTICE_BUFFER + Object.keys(state.answers).length) {
        const count = state.questions.length ? 1 : PRACTICE_BUFFER
        const incoming = await request(count, state.questions)
        if (disposed) return
        if (!Array.isArray(incoming) || incoming.length !== count) {
          throw new Error('The quiz service returned an incomplete batch.')
        }
        update({ questions: appendQuestions(state.questions, incoming), status: 'ready' })
      }
    } catch (error) {
      if (!disposed && error.name !== 'AbortError') {
        update(state.questions.length
          ? { backgroundError: error.message }
          : { error: error.message, status: 'error' })
      }
    } finally {
      busy = false
      if (!disposed) update({ pending: false })
    }
  }


  function answer(id, key) {
    if (disposed || state.answers[id]) return
    const question = state.questions.find((item) => item.id === id)
    if (!question?.options.some((option) => option.key === key)) return
    update({ answers: { ...state.answers, [id]: key } })
    void refill()
  }


  function select(index) {
    if (!disposed && index >= 0 && index < state.questions.length) update({ index })
  }

  return { start: () => { publish(state); void refill() }, answer, select,
    retry: () => { void refill() }, stop: () => { disposed = true } }
}
