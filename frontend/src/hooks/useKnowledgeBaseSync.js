import { useEffect, useRef } from 'react'


export function useKnowledgeBaseSync(apiUrl, documents, onDocuments, onError, refreshToken = 0) {
  const callbacks = useRef({ onDocuments, onError })
  useEffect(() => { callbacks.current = { onDocuments, onError } })
  const ids = documents.map((doc) => doc.documentId).filter(Boolean).join(',')
  useEffect(() => {
    const controller = new AbortController()
    let timer


    async function sync() {
      try {
        const response = await fetch(`${apiUrl}/documents/sync`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ knowledge_base_id: 'local', document_ids: ids ? ids.split(',') : [] }),
          signal: controller.signal,
        })
        if (!response.ok) throw new Error('Could not sync the knowledge base.')
        const payload = await response.json()
        if (controller.signal.aborted) return
        callbacks.current.onDocuments(payload.documents.map((doc) => ({
          documentId: doc.document_id, fileName: doc.filename,
          title: doc.filename.replace(/\.pdf$/i, ''), status: doc.status,
          pages: doc.pages, chunks: doc.chunks, hierarchy: doc.hierarchy,
        })))
        if (payload.missing_document_ids?.length) {
          callbacks.current.onError('Some saved PDFs could not be restored. Upload them again.')
        }
        if (payload.documents.some((doc) => doc.status === 'processing')) timer = setTimeout(sync, 3000)
      } catch (error) {
        if (error.name !== 'AbortError') timer = setTimeout(sync, 5000)
      }
    }
    sync()
    return () => { controller.abort(); clearTimeout(timer) }
  }, [apiUrl, ids, refreshToken])
}
