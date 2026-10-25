import { SourceCitation } from './pdf/SourceCitation.jsx'
import { QuizVerification } from './QuizVerification'


export function QuizExplanation({ question, isCorrect, scope }) {
  const answer = question.options.find((option) => option.isCorrect)

  return (
    <section
      className={`question-explanation ${isCorrect ? 'is-pass' : 'is-fail'}`}
      aria-label="Answer explanation and PDF sources"
    >
      <strong>{isCorrect ? '✓ Correct!' : '✕ Incorrect.'}</strong>
      <p className="explanation-answer">
        <strong>Correct answer: {answer.key}.</strong> {answer.text}
      </p>
      <p className="explanation-text">{question.explanation}</p>

      <div className="explanation-sources">
        <strong>From your PDF</strong>
        <p className="explanation-page-note">PDF page numbers count from the first page of the file.</p>
        <ul className="explanation-source-list">
          {question.sources.map((source, index) => (
            <li key={`${source.document_id}-${source.page}-${index}`}>
              <SourceCitation source={source}>
                {source.filename} · PDF page {source.page}
              </SourceCitation>
              <blockquote>{source.quote}</blockquote>
            </li>
          ))}
        </ul>
      </div>
      <QuizVerification key={question.id} question={question} scope={scope} />
    </section>
  )
}
