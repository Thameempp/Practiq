import { useRef } from 'react'
import { recallQuestion } from '../services/questionHistory.js'


export function useQuestionHistory(messages, conversationId, question, setQuestion) {
  const history = useRef({ index: -1, draft: '', version: null })


  const resetHistory = () => { history.current = { index: -1, draft: '', version: null } }


  function onHistoryKeyDown(event) {
    const questions = messages.filter((message) => message.role === 'user' && message.content)
    const version = `${conversationId}:${questions.at(-1)?.id}:${questions.length}`
    if (history.current.version !== version) resetHistory()
    const input = event.currentTarget
    const recalled = recallQuestion(questions.map((message) => message.content), question, {
      key: event.key, selectionStart: input.selectionStart, selectionEnd: input.selectionEnd,
      shiftKey: event.shiftKey, altKey: event.altKey, ctrlKey: event.ctrlKey,
      metaKey: event.metaKey, isComposing: event.nativeEvent.isComposing,
      keyCode: event.keyCode,
    }, history.current)
    if (!recalled) return false
    event.preventDefault()
    history.current = { ...recalled, version }
    setQuestion(recalled.value)
    requestAnimationFrame(() => {
      if (input.isConnected && input.value === recalled.value) {
        input.setSelectionRange(recalled.value.length, recalled.value.length)
      }
    })
    return true
  }

  return { onHistoryKeyDown, resetHistory }
}
