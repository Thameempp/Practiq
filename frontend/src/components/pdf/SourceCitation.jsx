import { usePdfViewer } from './viewerContext.js'
import './citations.css'


export function SourceCitation({ source, children }) {
  const open = usePdfViewer()
  const id = source?.id || source?.citation_id
  if (!id || !open) return <span>{children}</span>
  return <button type="button" className="source-citation"
    aria-label={`Open ${source.filename}, PDF page ${source.page}`}
    title={`${source.filename} · PDF page ${source.page}`}
    onClick={() => open({ id, knowledge_base_id: source.knowledge_base_id || 'local' })}>
    {children}
  </button>
}
