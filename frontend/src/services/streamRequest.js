import { readTextStream } from './readTextStream.js'
import { readEventStream } from './readEventStream.js'


export async function streamRequest({ url, body, signal, onText, onRoute, onProgress, onMetadata }) {
  const response = await fetch(url, { method: 'POST', headers: {
    'Content-Type': 'application/json', Accept: 'text/event-stream',
  },
    body: JSON.stringify(body), signal })
  if (signal.aborted) throw new DOMException('Aborted', 'AbortError')
  if (!response.ok) {
    const message = await response.text()
    let detail
    try { detail = JSON.parse(message).detail } catch { /* A plain-text error is also valid. */ }
    throw new Error(typeof detail === 'string' ? detail : message || `Request failed: ${response.status}`)
  }
  if (response.headers.get('content-type')?.includes('application/json')) {
    const route = await response.json()
    if (signal.aborted) throw new DOMException('Aborted', 'AbortError')
    const content = route.message || ''
    onText(content)
    onRoute?.(route)
    return content
  }
  return response.headers.get('content-type')?.includes('text/event-stream')
    ? readEventStream(response, onText, onProgress, signal, onMetadata) : readTextStream(response, onText, signal)
}
