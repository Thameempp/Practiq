import { useTextStream } from '../hooks/useTextStream'
import { buildQuizVerification } from '../services/quizVerification.js'
import { StreamingReply } from './StreamingReply'

import { API_URL } from '../services/apiConfig.js'


export function QuizVerification({ question, scope }) {
  const { store, isStreaming, error, startStream, stopStream } = useTextStream()
  return <div className="quiz-verification">
    <button className="quiz-nav-btn" type="button" disabled={isStreaming}
      onClick={() => startStream({ url: `${API_URL}/verify`, body: buildQuizVerification(question, scope) })}>
      {isStreaming ? 'Verifying…' : 'Verify answer and explanation'}
    </button>
    {isStreaming && <button className="quiz-nav-btn" type="button" onClick={stopStream}>Stop</button>}
    {error && <p role="alert">{error}</p>}
    <div className="markdown-content" aria-live="polite"><StreamingReply store={store} isStreaming={isStreaming} /></div>
  </div>
}
