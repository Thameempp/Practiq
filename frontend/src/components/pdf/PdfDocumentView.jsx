import { useCallback, useState } from 'react'
import { PdfPage } from './PdfPage.jsx'
import { usePdfDocument } from './usePdfDocument.js'


export function PdfDocumentView({ source }) {
  const { pdf, error } = usePdfDocument(source)
  const [position, setPosition] = useState(null), [zoom, setZoom] = useState(1)
  const page = position?.id === source.id ? position.page : source.page
  const [status, setStatus] = useState(null)
  const statusKey = `${source.id}:${page}:${zoom}`


  const onMatch = useCallback((text) => setStatus({ key: statusKey, text }), [statusKey])
  const match = status?.key === statusKey ? status.text : ''


  const goTo = (value) => setPosition({ id: source.id, page: Math.max(1, Math.min(pdf.numPages, Number(value) || 1)) })
  return <div className="pdf-document">
    <section className="pdf-preview" aria-label="Original PDF">
      {error ? <p role="alert" className="pdf-error">{error}</p> : !pdf ? <p role="status">Loading PDF…</p> : <>
        <nav className="pdf-toolbar" aria-label="PDF navigation">
          <button type="button" disabled={page <= 1} onClick={() => goTo(page - 1)} aria-label="Previous page">←</button>
          <label>Page <input type="number" min="1" max={pdf.numPages} value={page}
            onChange={(event) => goTo(event.target.value)} /></label><span>of {pdf.numPages}</span>
          <button type="button" disabled={page >= pdf.numPages} onClick={() => goTo(page + 1)} aria-label="Next page">→</button>
          <button type="button" disabled={zoom <= 0.5} onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))} aria-label="Zoom out">−</button>
          <output aria-label="Zoom">{Math.round(zoom * 100)}%</output>
          <button type="button" disabled={zoom >= 2.5} onClick={() => setZoom((z) => Math.min(2.5, z + 0.25))} aria-label="Zoom in">+</button>
        </nav>
        <div className="pdf-page-scroll" data-lenis-prevent>
          <PdfPage pdf={pdf} pageNumber={page} zoom={zoom}
            quote={page === source.page ? source.quote : ''} onMatch={onMatch} />
        </div>
      </>}
    </section>
    <aside className="pdf-source-details">
      <h3>Source passage</h3>
      <p>PDF page {source.page}{source.page_end > source.page ? `–${source.page_end}` : ''} of {source.page_count}</p>
      {source.quote ? <blockquote>{source.quote}</blockquote>
        : <p>This citation opens the source pages. It does not identify a single passage.</p>}
      <p className="pdf-match-status" role="status">{page !== source.page ? 'You are viewing another page.'
        : match || 'Opening the cited page…'}</p>
      {page !== source.page && <button type="button" onClick={() => goTo(source.page)}>Back to cited page</button>}
      <small>Page numbers count from the first page of the PDF.</small>
    </aside>
  </div>
}
