import { memo } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export const StreamingMessage = memo(function StreamingMessage({
  content,
  components,
}) {
  const normalizedContent = content.replace(/<br\s*\/?>/gi, '\n')

  return (
    <div className="streaming-message">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {normalizedContent}
      </ReactMarkdown>
    </div>
  )
})
