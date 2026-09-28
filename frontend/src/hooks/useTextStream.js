import { useCallback, useRef, useState } from 'react'

export function useTextStream() {
  const [text, setText] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState('')
  const abortControllerRef = useRef(null)

  const startStream = useCallback(async ({ url, body, onText, onComplete }) => {
    abortControllerRef.current?.abort()

    const controller = new AbortController()
    abortControllerRef.current = controller
    setText('')
    setError('')
    setIsStreaming(true)

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: controller.signal,
      })

      if (!response.ok) {
        const message = await response.text()
        throw new Error(message || `Request failed: ${response.status}`)
      }

      if (!response.body) {
        throw new Error('The response did not contain a readable stream.')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let accumulated = ''
      let pending = ''
      let frameId = null

      const flush = () => {
        frameId = null

        if (!pending) return

        accumulated += pending
        pending = ''
        setText(accumulated)
        onText?.(accumulated)
      }

      while (true) {
        const { value, done } = await reader.read()

        if (done) break

        pending += decoder.decode(value, { stream: true })

        if (frameId === null) {
          frameId = requestAnimationFrame(flush)
        }
      }

      pending += decoder.decode()

      if (frameId !== null) {
        cancelAnimationFrame(frameId)
        flush()
      } else if (pending) {
        flush()
      }

      onComplete?.(accumulated)
    } catch (streamError) {
      if (streamError.name !== 'AbortError') {
        setError(
          streamError.message || 'Could not read the streaming response.',
        )
      }
    } finally {
      if (abortControllerRef.current === controller) {
        abortControllerRef.current = null
      }
      setIsStreaming(false)
    }
  }, [])

  const stopStream = useCallback(() => {
    abortControllerRef.current?.abort()
    abortControllerRef.current = null
    setIsStreaming(false)
  }, [])

  return { text, isStreaming, error, startStream, stopStream }
}
