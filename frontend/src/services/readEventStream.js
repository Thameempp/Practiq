export async function readEventStream(response, onText, onProgress, signal, onMetadata) {
  if (!response.body) throw new Error('The response did not contain a readable stream.')
  const reader = response.body.getReader(), decoder = new TextDecoder()
  let pending = '', text = '', completed = false


  const cancel = () => { reader.cancel().catch(() => {}) }
  signal.addEventListener('abort', cancel, { once: true })


  const frame = (source) => {
    if (signal.aborted) return
    const lines = source.split('\n')
    const event = lines.find((line) => line.startsWith('event:'))?.slice(6).trim()
    const data = lines.filter((line) => line.startsWith('data:')).map((line) => line.slice(5).trimStart()).join('\n')
    if (!data || !event) return
    const value = JSON.parse(data)
    if (event === 'error') throw new Error(value)
    if (event === 'progress') onProgress?.(value)
    if (event === 'sources' || event === 'citation' || event === 'agent') onMetadata?.(event, value)
    if (event === 'text') { text += value; onText(text) }
    if (event === 'done') completed = true
  }
  try {
    if (signal.aborted) cancel()
    while (!signal.aborted) {
      const { value, done } = await reader.read()
      if (signal.aborted) break
      pending += done ? decoder.decode() : decoder.decode(value, { stream: true })
      pending = pending.replace(/\r\n/g, '\n')
      let boundary
      while ((boundary = pending.indexOf('\n\n')) !== -1) {
        frame(pending.slice(0, boundary))
        pending = pending.slice(boundary + 2)
      }
      if (done) break
    }
    if (!signal.aborted && !completed) throw new Error('The response was interrupted. Please try again.')
    return text
  } finally {
    signal.removeEventListener('abort', cancel)
    if (!completed) await reader.cancel().catch(() => {})
    reader.releaseLock()
  }
}
