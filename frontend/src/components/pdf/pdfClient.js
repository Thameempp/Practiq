import { getDocument, GlobalWorkerOptions } from 'pdfjs-dist'
import workerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url'

GlobalWorkerOptions.workerSrc = workerUrl
import { API_URL } from '../../services/apiConfig.js'


export function pdfApiUrl(path, knowledgeBase = 'local') {
  return `${API_URL}${path}?knowledge_base_id=${encodeURIComponent(knowledgeBase)}`
}


export function loadPdf(source) {
  const assets = new URL(`${import.meta.env.BASE_URL}pdf-assets/`, window.location.href).href
  return getDocument({
    url: pdfApiUrl(`/documents/${encodeURIComponent(source.document_id)}/pdf`, source.knowledge_base_id),
    // Fetch only the ranges needed for the displayed page in a large document.
    disableAutoFetch: true, disableStream: true, rangeChunkSize: 65536,
    isEvalSupported: false,
    cMapUrl: `${assets}cmaps/`, cMapPacked: true,
    standardFontDataUrl: `${assets}standard_fonts/`, wasmUrl: `${assets}wasm/`,
    iccUrl: `${assets}iccs/`,
  })
}
