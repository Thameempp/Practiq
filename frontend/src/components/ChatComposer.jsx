import { useQuestionHistory } from '../hooks/useQuestionHistory.js'


export function ChatComposer({ question, setQuestion, messages, conversationId, scope,
  isStreaming, onSubmit, onStop, onNewChat }) {
  const { onHistoryKeyDown, resetHistory } = useQuestionHistory(messages, conversationId, question, setQuestion)
  const hasQuestion = Boolean(question.trim())
  return <>
    <form className="composer" onSubmit={onSubmit}>
      <textarea value={question} onChange={(event) => {
        resetHistory()
        setQuestion(event.target.value)
      }} onKeyDown={(event) => {
        if (onHistoryKeyDown(event)) return
        if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing && event.keyCode !== 229) onSubmit(event)
      }} placeholder={scope ? `Ask specifically about ${scope.title}...` : 'Ask anything across your documents...'}
        aria-label="Question" rows="1" />
      {isStreaming ? <button className="stop-button composer-action" type="button" onClick={onStop}>Stop</button>
        : <button className={`send-button composer-action${hasQuestion ? '' : ' is-empty'}`}
          type="submit" disabled={!hasQuestion} tabIndex={hasQuestion ? 0 : -1} aria-hidden={!hasQuestion}>
          Ask <span aria-hidden="true">↗</span>
        </button>}
    </form>
    <div className="composer-footer">
      <p className="composer-note">Enter to ask · Shift + Enter for a new line · ↑ previous question</p>
      {messages.length > 0 && <button className="new-chat-button" type="button" onClick={onNewChat}>New chat</button>}
    </div>
  </>
}
