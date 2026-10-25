import { useEffect, useRef } from 'react'
import './pdfViewer.css'


export function PdfViewerDialog({ title = 'PDF source', onClose, children }) {
  const dialog = useRef(null)
  useEffect(() => {
    const element = dialog.current
    element.showModal()
    const previous = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      element.close()
      document.body.style.overflow = previous
    }
  }, [])
  return <dialog ref={dialog} className="pdf-dialog" aria-labelledby="pdf-dialog-title" data-lenis-prevent
    onCancel={(event) => { event.preventDefault(); onClose() }}
    onClick={(event) => { if (event.target === event.currentTarget) onClose() }}>
    <header className="pdf-dialog-header">
      <h2 id="pdf-dialog-title">{title}</h2>
      <button type="button" aria-label="Close PDF viewer" onClick={onClose} autoFocus>Close ×</button>
    </header>
    {children}
  </dialog>
}
