export function recallQuestion(questions, value, event, state) {
  const { key, selectionStart, selectionEnd } = event
  if (!['ArrowUp', 'ArrowDown'].includes(key) || event.isComposing || event.keyCode === 229
    || event.shiftKey || event.altKey || event.ctrlKey || event.metaKey
    || selectionStart !== selectionEnd || !questions.length) return null

  const older = key === 'ArrowUp'
  if (older ? value.slice(0, selectionStart).includes('\n')
    : value.slice(selectionEnd).includes('\n') || state.index < 0) return null

  const draft = state.index < 0 ? value : state.draft
  const index = older ? Math.min(state.index + 1, questions.length - 1) : state.index - 1
  return { index, draft, value: index < 0 ? draft : questions[questions.length - 1 - index] }
}
