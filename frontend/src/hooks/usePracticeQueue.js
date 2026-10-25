import { useEffect, useRef, useState } from 'react'
import { createPracticeQueue } from '../services/practiceQueue.js'
import { requestPractice } from '../services/practiceApi.js'
import { practiceState } from '../services/practiceState.js'
import { loadPractice, practiceCacheKey, savePractice } from '../services/practiceStorage.js'


export function usePracticeQueue(documentId, scope) {
  const [state, setState] = useState(() => practiceState())
  const queue = useRef(null)
  const scopeKey = JSON.stringify(scope || null)
  const cacheKey = practiceCacheKey(documentId, scope)

  useEffect(() => {
    if (!documentId) return
    const controller = new AbortController()
    const saved = loadPractice(cacheKey)
    const session = createPracticeQueue(saved,
      (count, previous) => requestPractice(documentId, JSON.parse(scopeKey), count,
        [...(saved.excluded || []), ...previous], controller.signal),
      (next) => { setState(next); savePractice(cacheKey, next) })
    queue.current = session
    session.start()
    return () => { session.stop(); controller.abort() }
  }, [documentId, scopeKey, cacheKey])

  return { ...state, answer: (id, key) => queue.current?.answer(id, key),
    select: (index) => queue.current?.select(index), retry: () => queue.current?.retry() }
}
