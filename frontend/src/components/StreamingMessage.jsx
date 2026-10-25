import { memo, useMemo } from 'react'
import { SourceCitation } from './pdf/SourceCitation.jsx'
import { MarkdownBlock } from './MarkdownBlock.jsx'
import { sourceLabel } from '../services/markdownContent.js'


export const StreamingMessage = memo(function StreamingMessage({
  content,
  components,
  isStreaming = false,
  blocks = [],
  tail = '',
  sources = {}, citations = {},
}) {
  const renderers = useMemo(() => ({ ...components, a: function SourceLink({ href, children }) {
    if (href?.startsWith('#source-')) {
      const id = href.slice(8)
      return sources[id] ? <SourceCitation source={sources[id]}>{sourceLabel(id, sources, citations)}</SourceCitation>
        : <span>{children}</span>
    }
    return <a href={href} target="_blank" rel="noreferrer">{children}</a>
  } }), [components, sources, citations])

  return (
    <div className="streaming-message">
      {isStreaming ? <>
        {blocks.map((block) => <MarkdownBlock key={block.id} content={block.text} components={renderers}
          sources={sources} citations={citations} />)}
        {tail && <div className="streaming-markdown-tail"><MarkdownBlock content={tail} components={renderers}
          sources={sources} citations={citations} /></div>}
      </> : <MarkdownBlock content={content} components={renderers} sources={sources} citations={citations} />}
    </div>
  )
})
