import { useEffect, useState } from 'react'
import { loadPdf } from './pdfClient.js'


export function usePdfDocument(source) {
  const [loaded, setLoaded] = useState(null)
  const { document_id, knowledge_base_id } = source
  const key = `${knowledge_base_id}:${document_id}`
  useEffect(() => {
    let active = true
    const task = loadPdf({ document_id, knowledge_base_id })
    task.promise.then((pdf) => { if (active) setLoaded({ key, pdf }) })
      .catch(() => { if (active) setLoaded({ key, error: 'Could not load the original PDF. It may have been removed. Try reopening the source.' }) })
    return () => { active = false; task.destroy().catch(() => {}) }
  }, [document_id, knowledge_base_id, key])
  return loaded?.key === key ? loaded : { pdf: null, error: '' }
}
