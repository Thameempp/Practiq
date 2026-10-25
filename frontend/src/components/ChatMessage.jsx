import { memo } from 'react'
import { DocumentChoices } from './DocumentChoices'
import { StreamingMessage } from './StreamingMessage'
import { StreamingReply } from './StreamingReply'
import { ActiveAgentLabel } from './ActiveAgentLabel'


export const ChatMessage = memo(function ChatMessage({
  message, generating, choicesDisabled, store, components, onSelectDocument, onLayout,
}) {
  return <article className={`message ${message.role}`}>
    <span className="message-role">{message.role === 'user' ? 'YOU' : <>
      <span className="message-role-heading">PDF
        {generating && <span className="role-generating-dots" aria-label="Generating response">
          <span /><span /><span />
        </span>}
      </span>
      {generating && <ActiveAgentLabel store={store} />}
    </>}</span>
    {message.role === 'assistant' ? <div className="markdown-content">
      {generating ? <StreamingReply store={store} components={components} onLayout={onLayout} />
        : <StreamingMessage content={message.content} components={components}
          sources={message.sources} citations={message.citations} />}
      <DocumentChoices documents={message.documentChoices} disabled={choicesDisabled} onSelect={onSelectDocument} />
    </div> : <div className="user-message-container">
      {message.scope && <div className="user-message-scope-tag">
        <span>🎯 Scope: {message.scope.title} ({message.scope.pageLabel})</span>
      </div>}
      <p>{message.content}</p>
    </div>}
  </article>
})
