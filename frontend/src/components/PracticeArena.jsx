import { QuizExplanation } from './QuizExplanation'
import { usePracticeQueue } from '../hooks/usePracticeQueue.js'


export function PracticeArena({ node, documentId, scope }) {
  const {
    questions: quiz, answers: selectedAnswers, index: quizIndex,
    status, error, pending, backgroundError, answer, select, retry,
  } = usePracticeQueue(documentId, scope)
  const title = node?.title || 'Selected section'

  // Score calculation
  const totalQuestions = quiz.length
  const answeredCount = Object.keys(selectedAnswers).length
  const firstVisible = Math.max(0, Math.min(quizIndex - 2, totalQuestions - 5))
  const visibleQuestions = quiz.slice(firstVisible, firstVisible + 5)
  const score = quiz.reduce((acc, q) => {
    const chosen = selectedAnswers[q.id]
    const correctOpt = q.options.find((opt) => opt.isCorrect)
    return chosen === correctOpt?.key ? acc + 1 : acc
  }, 0)

  const currentQuestion = quiz[quizIndex] || quiz[0]
  const currentChoice = currentQuestion ? selectedAnswers[currentQuestion.id] : null
  const isCurrentAnswered = Boolean(currentChoice)
  const correctOpt = currentQuestion?.options.find((opt) => opt.isCorrect)


  function handleSelectOption(questionId, optionKey) {
    answer(questionId, optionKey)
  }


  function handlePrevQuestion() {
    select(Math.max(0, quizIndex - 1))
  }


  function handleNextQuestion() {
    select(Math.min(totalQuestions - 1, quizIndex + 1))
  }

  if (documentId && status === 'loading') {
    return (
      <div className="practice-arena" role="status" aria-label={`Generating practice for ${title}`}>
        <div className="practice-body">
          <p className="empty-hint">Generating questions from this section...</p>
        </div>
      </div>
    )
  }

  if (!documentId || status === 'error') {
    return (
      <div className="practice-arena" role="alert">
        <div className="practice-body">
          <p className="error-message">{error || 'Upload a document before starting practice.'}</p>
          <button
            type="button"
            className="quiz-nav-btn is-primary is-ready"
            onClick={retry}
            disabled={!documentId}
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="practice-arena" role="region" aria-label={`Practice for ${title}`}>
      {/* Main MCQ Practice Area (1 at a time) */}
      <div className="practice-body">
        {currentQuestion && (
          <div className="practice-quiz-view">
            {/* Top Question Progress & Score Bar */}
            <div className="practice-quiz-topbar">
              <div className="quiz-pills-nav" role="tablist" aria-label="Question selector">
                {visibleQuestions.map((q, offset) => {
                  const idx = firstVisible + offset
                  const answered = selectedAnswers[q.id]
                  const qCorrect = q.options.find((opt) => opt.isCorrect)
                  const isCorrect = answered === qCorrect?.key
                  const isActive = idx === quizIndex

                  let statusClass = ''
                  if (answered) {
                    statusClass = isCorrect ? 'is-answered-correct' : 'is-answered-wrong'
                  }

                  return (
                    <button
                      type="button"
                      key={q.id}
                      className={`quiz-pill-btn ${isActive ? 'is-active' : ''} ${statusClass}`}
                      onClick={() => select(idx)}
                      title={`Jump to Question ${idx + 1}`}
                    >
                      <span>Q{idx + 1}</span>
                      {answered && (
                        <span className="pill-dot" aria-hidden="true" />
                      )}
                    </button>
                  )
                })}
              </div>

              <div className="quiz-topbar-right">
                <span className="quiz-score-tag">
                  Score: <strong>{score}</strong> / {answeredCount}
                </span>
                <span className="practice-queue-status" role="status">
                  {pending ? 'Preparing next question…' : ''}
                </span>
              </div>
            </div>

            {/* Single MCQ Area (unboxed) */}
            <div className="practice-question-card is-single-view" key={currentQuestion.id}>
              <div className="question-header">
                <p className="question-text">{currentQuestion.question}</p>
              </div>

              <div className="question-options">
                {currentQuestion.options.map((opt) => {
                  const isChosen = currentChoice === opt.key
                  let optionClass = 'quiz-option-btn'

                  if (isCurrentAnswered) {
                    if (opt.isCorrect) {
                      optionClass += ' is-correct'
                    } else if (isChosen) {
                      optionClass += ' is-incorrect'
                    } else {
                      optionClass += ' is-dimmed'
                    }
                  }

                  return (
                    <button
                      type="button"
                      key={opt.key}
                      className={optionClass}
                      onClick={() => handleSelectOption(currentQuestion.id, opt.key)}
                      disabled={isCurrentAnswered}
                    >
                      <span className="option-key">{opt.key}</span>
                      <span className="option-text">{opt.text}</span>
                      {isCurrentAnswered && opt.isCorrect && (
                        <span className="option-feedback-icon" aria-label="Correct">✓</span>
                      )}
                      {isCurrentAnswered && isChosen && !opt.isCorrect && (
                        <span className="option-feedback-icon" aria-label="Incorrect">✕</span>
                      )}
                    </button>
                  )
                })}
              </div>

              {/* Instant Answer Explanation */}
              {isCurrentAnswered && (
                <QuizExplanation
                  scope={scope}
                  question={currentQuestion}
                  isCorrect={currentChoice === correctOpt?.key}
                />
              )}

              {/* Navigation Controls for Single Question */}
              <div className="question-nav-controls">
                <button
                  type="button"
                  className="quiz-nav-btn"
                  onClick={handlePrevQuestion}
                  disabled={quizIndex === 0}
                >
                  ← Prev
                </button>

                <span className="question-step-indicator">
                  Question {quizIndex + 1} of {totalQuestions}
                </span>

                <button
                  type="button"
                  className={`quiz-nav-btn is-primary ${isCurrentAnswered ? 'is-ready' : ''}`}
                  onClick={handleNextQuestion}
                  disabled={quizIndex >= totalQuestions - 1}
                >
                  {quizIndex >= totalQuestions - 1 && pending ? 'Preparing…' : 'Next Question →'}
                </button>
              </div>
            </div>

            {backgroundError && (
              <p className="practice-queue-status" role="status">{backgroundError} Your current questions are still available.</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
