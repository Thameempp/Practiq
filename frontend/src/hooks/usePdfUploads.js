import { useEffect, useRef, useState } from 'react'
import { uploadPdfFile } from '../services/documentsApi.js'
import { createUploadQueue } from '../services/uploadQueue.js'


export function usePdfUploads(apiUrl, onUploaded, onError) {
  const [pending, setPending] = useState(0)
  const mounted = useRef(false)
  const queue = useRef(null)
  const callbacks = useRef({ onUploaded, onError })
  useEffect(() => {
    callbacks.current = { onUploaded, onError }
  })

  useEffect(() => {
    mounted.current = true
    const controller = new AbortController()
    queue.current = createUploadQueue((file) => uploadPdfFile(apiUrl, file, controller.signal))
    return () => {
      mounted.current = false
      controller.abort()
    }
  }, [apiUrl])


  function uploadFiles(files) {
    const batch = Array.from(files)
    if (!batch.length) return
    onError('')
    setPending((count) => count + batch.length)
    for (const file of batch) {
      queue.current(file)
        .then((document) => {
          if (mounted.current && document) {
            callbacks.current.onUploaded(document)
          }
        })
        .catch((error) => {
          if (mounted.current && error.name !== 'AbortError') {
            callbacks.current.onError(error.message || 'Could not upload the PDF.')
          }
        })
        .finally(() => {
          if (mounted.current) {
            setPending((count) => count - 1)
          }
        })
    }
  }

  return { isUploading: pending > 0, uploadFiles }
}
