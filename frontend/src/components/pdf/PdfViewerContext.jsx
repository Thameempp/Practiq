import { lazy, Suspense, useCallback, useRef, useState } from 'react'
import { PdfViewerContext } from './viewerContext.js'
import { PdfViewerBoundary } from './PdfViewerBoundary.jsx'

const Viewer = lazy(() => import('./PdfViewer.jsx'))


export function PdfViewerProvider({ children }) {
  const [active, setActive] = useState(null)
  const trigger = useRef(null)


  const open = useCallback((source) => {
    trigger.current = document.activeElement
    setActive(source)
  }, [])


  const close = useCallback(() => {
    setActive(null)
    requestAnimationFrame(() => trigger.current?.focus())
  }, [])
  return <PdfViewerContext.Provider value={open}>
    {children}
    {active && <PdfViewerBoundary key={active.id} onClose={close}>
      <Suspense fallback={<p role="status" className="pdf-opening">Opening PDF viewer…</p>}>
        <Viewer reference={active} onClose={close} />
      </Suspense>
    </PdfViewerBoundary>}
  </PdfViewerContext.Provider>
}
