import { useMemo, useState } from 'react'
import { getPracticeForNode } from '../data/practiceData'

export function PracticeArena({ node }) {
  const [quizIndex, setQuizIndex] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState({}) // { [questionId]: optionKey }

  const practice = useMemo(() => {
    return getPracticeForNode(node)
  }, [node])

  if (!practice) {
    return null
  }

  const { quiz, title } = practice

  // Score calculation
  const totalQuestions = quiz.length
  const answeredCount = Object.keys(selectedAnswers).length
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
    if (selectedAnswers[questionId]) return
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: optionKey,
    }))
  }

  function handlePrevQuestion() {
    setQuizIndex((prev) => Math.max(0, prev - 1))
  }

  function handleNextQuestion() {
    setQuizIndex((prev) => Math.min(totalQuestions - 1, prev + 1))
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
                {quiz.map((q, idx) => {
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
                      onClick={() => setQuizIndex(idx)}
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
                  Score: <strong>{score}</strong> / {totalQuestions}
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
                <div className={`question-explanation ${currentChoice === correctOpt?.key ? 'is-pass' : 'is-fail'}`}>
                  <strong>{currentChoice === correctOpt?.key ? '✓ Correct!' : '✕ Key Principle:'}</strong>{' '}
                  <span>{currentQuestion.explanation}</span>
                </div>
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
                  Next Question →
                </button>
              </div>
            </div>

            {/* Quiz Completion Banner if all answered */}
            {answeredCount === totalQuestions && (
              <div className="quiz-completion-banner">
                <div className="completion-copy">
                  <strong>🎯 Practice Complete!</strong> You scored {score} of {totalQuestions} ({Math.round((score / totalQuestions) * 100)}%).
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
