import { useEffect, useRef, useState } from 'react'
import { TextLayer } from 'pdfjs-dist'
import { highlightPassage } from './highlightPassage.js'
import './pdfTextLayer.css'


export function PdfPage({ pdf, pageNumber, zoom, quote, onMatch }) {
  const surface = useRef(null)
  const [width, setWidth] = useState(0)
  const [failure, setFailure] = useState(null)
  const renderKey = `${pageNumber}:${zoom}:${width}:${quote}`
  const error = failure?.key === renderKey ? failure.message : ''
  useEffect(() => {
    const parent = surface.current.parentElement
    const observer = new ResizeObserver(() => {
      const style = getComputedStyle(parent)
      setWidth(parent.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight))
    })
    observer.observe(parent)
    return () => observer.disconnect()
  }, [])
  useEffect(() => {
    const host = surface.current
    let cancelled = false, render, layer, page
    const canvas = document.createElement('canvas'), text = document.createElement('div')
    const overlay = document.createElement('div')
    text.className = 'textLayer'
    overlay.className = 'pdf-passage-overlay'
    overlay.setAttribute('aria-hidden', 'true')
    host.replaceChildren(canvas, text, overlay)


    async function draw() {
      page = await pdf.getPage(pageNumber)
      if (cancelled) return
      onMatch('Rendering the cited page…')
      const natural = page.getViewport({ scale: 1 })
      const viewport = page.getViewport({ scale: zoom * (width > 0 ? Math.min(1, width / natural.width) : 1) })
      const ratio = Math.min(window.devicePixelRatio || 1, 2)
      host.style.width = `${viewport.width}px`
      host.style.height = `${viewport.height}px`
      host.style.setProperty('--total-scale-factor', viewport.scale * viewport.userUnit)
      canvas.width = Math.ceil(viewport.width * ratio)
      canvas.height = Math.ceil(viewport.height * ratio)
      canvas.style.width = `${viewport.width}px`
      canvas.style.height = `${viewport.height}px`
      render = page.render({ canvasContext: canvas.getContext('2d'), viewport,
        transform: ratio === 1 ? null : [ratio, 0, 0, ratio, 0, 0] })
      await render.promise
      if (cancelled) return
      layer = new TextLayer({ textContentSource: await page.getTextContent(), container: text, viewport })
      if (cancelled) return
      await layer.render()
      if (cancelled) return
      const found = quote && highlightPassage(layer, quote, host, overlay)
      onMatch(found ? `Highlighted source passage · Page ${pageNumber}`
        : quote ? 'Page opened. The passage could not be matched uniquely; no highlight was applied.' : 'Source page opened.')
    }
    draw().catch((failure) => {
      if (!cancelled && failure.name !== 'RenderingCancelledException') setFailure({ key: renderKey,
        message: 'Could not render this page. Try another page or reopen the source.' })
    })
    return () => { cancelled = true; render?.cancel(); layer?.cancel(); host.replaceChildren() }
  }, [pdf, pageNumber, zoom, width, quote, onMatch, renderKey])
  return <>{error && <p className="pdf-error" role="alert">{error}</p>}
    <div ref={surface} className="pdf-page-surface" aria-label={`PDF page ${pageNumber}`} /></>
}
