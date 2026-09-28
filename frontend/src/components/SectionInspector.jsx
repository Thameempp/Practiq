import { useState } from 'react'

export function SectionInspector({
  node,
  onClose,
  onScopeToggle,
  isScoped,
  onActionPrompt,
}) {
  const [copied, setCopied] = useState(false)

  if (!node) return null

  function handleCopy() {
    if (!node.excerpt) return
    navigator.clipboard.writeText(node.excerpt).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    }).catch(() => {})
  }

  return (
    <div className="inspector-backdrop" onClick={onClose}>
      <aside
        className="inspector-drawer"
        role="dialog"
        aria-modal="true"
        aria-label={`Inspect ${node.title}`}
        onClick={(e) => e.stopPropagation()}
      >
        <header className="inspector-header">
          <div className="inspector-meta">
            <span className="inspector-type">{node.type.toUpperCase()}</span>
            <span className="inspector-page">{node.pageLabel || `p. ${node.page}`}</span>
            {node.semanticTag && (
              <span className="inspector-tag">{node.semanticTag}</span>
            )}
          </div>
          <button
            type="button"
            className="inspector-close"
            onClick={onClose}
            aria-label="Close section inspector"
          >
            ✕
          </button>
        </header>

        <h3 className="inspector-title">{node.title}</h3>
        {node.summary && <p className="inspector-summary">{node.summary}</p>}

        <div className="inspector-actions">
          <button
            type="button"
            className={`inspector-btn ${isScoped ? 'is-active' : ''}`}
            onClick={() => onScopeToggle(node)}
          >
            {isScoped ? '✓ Scoped for RAG' : '🎯 Scope RAG to this'}
          </button>
          <button
            type="button"
            className="inspector-btn"
            onClick={() => onActionPrompt(`Summarize "${node.title}" in 3 concise bullet points with key insights.`)}
          >
            ⚡ Summarize
          </button>
          <button
            type="button"
            className="inspector-btn"
            onClick={() => onActionPrompt(`Explain "${node.title}" in simple terms using a real-world analogy.`)}
          >
            💡 Explain simply
          </button>
          <button
            type="button"
            className="inspector-btn"
            onClick={handleCopy}
          >
            {copied ? '✓ Copied' : '📋 Copy text'}
          </button>
        </div>

        {node.keywords && node.keywords.length > 0 && (
          <div className="inspector-keywords">
            <span className="inspector-keywords-label">INDEXED TOPICS:</span>
            <div className="inspector-chips">
              {node.keywords.map((kw, i) => (
                <button
                  key={i}
                  type="button"
                  className="inspector-chip"
                  onClick={() => onActionPrompt(`How does "${kw}" relate to ${node.title}?`)}
                  title={`Ask about ${kw}`}
                >
                  #{kw}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="inspector-body">
          <div className="inspector-body-label">VERBATIM DOCUMENT EXCERPT</div>
          <pre className="inspector-excerpt">{node.excerpt}</pre>
        </div>
      </aside>
    </div>
  )
}

