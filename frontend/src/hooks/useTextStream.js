import { useCallback, useEffect, useRef, useState } from 'react'
import { createStreamStore } from '../services/streamStore.js'
import { streamRequest } from '../services/streamRequest.js'


export function useTextStream() {
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState('')
  const active = useRef(null)
  const [store] = useState(createStreamStore)


  const settle = useCallback((request) => {
    if (active.current !== request) return
    store.finish()
    active.current = null
    setIsStreaming(false)
    const { sources, citations } = store.getSnapshot()
    request.onSettled?.(store.getText(), { sources, citations })
  }, [store])


  const stopStream = useCallback(() => {
    const request = active.current
    if (!request) return
    request.controller.abort()
    settle(request)
  }, [settle])


  const startStream = useCallback(async ({ url, body, onComplete, onRoute, onSettled }) => {
    stopStream()
    store.reset()
    const request = { controller: new AbortController(), onSettled }
    active.current = request
    setError('')
    setIsStreaming(true)


    const current = () => active.current === request && !request.controller.signal.aborted
    try {
      const content = await streamRequest({ url, body, signal: request.controller.signal,
        onText: (value) => { if (current()) store.update(value) },
        onRoute: (route) => { if (current()) onRoute?.(route) },
        onProgress: (update) => { if (current() && typeof update?.label === 'string') store.setStatus(update.label) },
        onMetadata: (kind, value) => { if (current()) store.metadata(kind, value) },
      })
      if (current()) {
        store.finish()
        onComplete?.(content)
      }
    } catch (streamError) {
      if (current() && streamError.name !== 'AbortError') {
        setError(streamError.message || 'Could not read the response.')
      }
    } finally {
      settle(request)
    }
  }, [settle, stopStream, store])
  useEffect(() => () => {
    active.current?.controller.abort()
    active.current = null
    store.discard()
  }, [store])
  return { store, isStreaming, error, startStream, stopStream }
}
