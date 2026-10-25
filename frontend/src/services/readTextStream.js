export async function readTextStream(response, onText, signal) {
  if (!response.body) throw new Error('The response did not contain a readable stream.')
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let text = ''


  const cancel = () => { reader.cancel().catch(() => {}) }
  signal.addEventListener('abort', cancel, { once: true })
  try {
    if (signal.aborted) cancel()
    while (!signal.aborted) {
      const { value, done } = await reader.read()
      if (done || signal.aborted) break
      text += decoder.decode(value, { stream: true })
      onText(text)
    }
    if (!signal.aborted) {
      text += decoder.decode()
      onText(text)
    }
    return text
  } finally {
    signal.removeEventListener('abort', cancel)
    reader.releaseLock()
  }
}
