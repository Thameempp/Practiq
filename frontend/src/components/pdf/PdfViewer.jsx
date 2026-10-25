import { useEffect, useState } from 'react'
import { PdfDocumentView } from './PdfDocumentView.jsx'
import { pdfApiUrl } from './pdfClient.js'
import { PdfViewerDialog } from './PdfViewerDialog.jsx'


export default function PdfViewer({ reference, onClose }) {
  const [resolved, setResolved] = useState(null)
  const source = resolved?.id === reference.id ? resolved.source : null
  const error = resolved?.id === reference.id ? resolved.error : ''
  useEffect(() => {
    const controller = new AbortController()
    fetch(pdfApiUrl(`/citations/${encodeURIComponent(reference.id)}`, reference.knowledge_base_id),
      { signal: controller.signal }).then(async (response) => {
      const result = await response.json()
      if (!response.ok) throw new Error(result.detail || 'This source is unavailable.')
      if (!controller.signal.aborted) setResolved({ id: reference.id, source: result })
    }).catch((failure) => {
      if (!controller.signal.aborted) setResolved({ id: reference.id, error: failure.message })
    })
    return () => controller.abort()
  }, [reference])
  return <PdfViewerDialog title={source?.filename} onClose={onClose}>
    {error ? <p className="pdf-error" role="alert">{error}</p>
      : source ? <PdfDocumentView source={source} /> : <p role="status">Resolving source…</p>}
  </PdfViewerDialog>
}
