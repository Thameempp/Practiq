import { createMarkdownBlocks } from './markdownBlocks.js'
import { citationMetadata } from './citationMetadata.js'


// Only the active reply subscribes; token updates never enter conversation state.
export function createStreamStore({ delay = 35, schedule = setTimeout, cancel = clearTimeout } = {}) {
  let visible = '', pending = '', timer = null
  const parser = createMarkdownBlocks()
  let snapshot = { content: '', blocks: [], tail: '', status: '', agents: [], sources: {}, citations: {} }
  const listeners = new Set()


  const clear = () => {
    if (timer !== null) cancel(timer)
    timer = null
  }


  const flush = () => {
    clear()
    if (visible === pending) return
    visible = pending
    snapshot = { ...snapshot, content: visible, ...parser.update(visible) }
    listeners.forEach((listener) => listener())
  }


  const setStatus = (status) => {
    if (snapshot.status === status) return
    snapshot = { ...snapshot, status }
    listeners.forEach((listener) => listener())
  }
  return {
    subscribe(listener) { listeners.add(listener); return () => listeners.delete(listener) },
    getSnapshot: () => snapshot,
    getText: () => visible,
    setStatus,


    metadata(kind, value) {
      if (kind === 'agent') {
        if (!value?.id || typeof value.name !== 'string' || !['started', 'finished'].includes(value.state)) return
        const agents = snapshot.agents.filter(({ id }) => id !== value.id)
        if (value.state === 'started') agents.push({ id: value.id, name: value.name })
        snapshot = { ...snapshot, agents }
        listeners.forEach((listener) => listener())
        return
      }
      const next = kind === 'sources'
        ? { ...snapshot, sources: { ...snapshot.sources, ...Object.fromEntries(
          (Array.isArray(value) ? value : []).filter((item) => item?.id).map((item) => [item.id, item]),
        ) } } : { ...snapshot, citations: { ...snapshot.citations, [value?.id]: value } }
      snapshot = { ...snapshot, ...citationMetadata(next) }
      listeners.forEach((listener) => listener())
    },


    update(content) {
      pending = content
      if (!visible) flush() // Show the first text without waiting for a batch.
      else if (timer === null) timer = schedule(flush, delay)
    },


    finish() {
      flush()
      if (!snapshot.agents.length) return
      snapshot = { ...snapshot, agents: [] }
      listeners.forEach((listener) => listener())
    },


    reset() {
      clear(); pending = ''; flush()
      snapshot = { ...snapshot, status: '', agents: [], sources: {}, citations: {} }
      listeners.forEach((listener) => listener())
    },


    discard() { clear(); pending = visible },
  }
}
