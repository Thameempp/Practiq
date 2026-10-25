import assert from 'node:assert/strict'
import test from 'node:test'
import { citationMetadata } from './citationMetadata.js'
import { createStreamStore } from './streamStore.js'
import { compactMessages } from './chatSession.js'

const id = 'c' + 'a'.repeat(24)
const source = { id, document_id: 'doc', filename: 'Notes.pdf', page: 2, quote: 'Original text' }
const citation = { id, label: '1' }

test('only server-known source IDs retain citation metadata', () => {
  const value = citationMetadata({ sources: { [id]: source }, citations: { [id]: citation } })
  assert.equal(value.sources[id].page, 2)
  assert.deepEqual(value.citations[id], citation)
  assert.deepEqual(citationMetadata({ sources: { arbitrary: { ...source, id: 'fake', url: 'https://evil' } },
    citations: { [id]: citation } }), { sources: {}, citations: {} })
})

test('stream metadata is available before text, merges documents and resets between replies', () => {
  const store = createStreamStore()
  store.metadata('sources', [source])
  store.metadata('citation', citation)
  assert.equal(store.getText(), '')
  assert.equal(store.getSnapshot().citations[id].label, '1')
  store.update(`Answer [1](#source-${id})`)
  const message = { ...store.getSnapshot(), role: 'assistant', id: 'a' }
  const saved = compactMessages([{ id: 'u', role: 'user', content: 'Question' }, message])
  assert.equal(saved[1].sources[id].page, 2)
  assert.equal(saved[1].citations[id].label, '1')
  store.reset()
  assert.deepEqual(store.getSnapshot().sources, {})
  assert.deepEqual(store.getSnapshot().citations, {})
})
