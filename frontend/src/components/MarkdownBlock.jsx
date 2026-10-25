import { memo, useMemo } from 'react'
import ReactMarkdown from 'react-markdown'
import { normalizeMarkdown, markdownPlugins, mathPlugins } from '../services/markdownContent.js'
import 'katex/dist/katex.min.css'


export const MarkdownBlock = memo(function MarkdownBlock({ content, components, sources, citations }) {
  const markdown = useMemo(() => normalizeMarkdown(content, sources, citations), [content, sources, citations])
  return <ReactMarkdown remarkPlugins={markdownPlugins} rehypePlugins={mathPlugins}
    components={components}>{markdown}</ReactMarkdown>
})
