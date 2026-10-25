import assert from 'node:assert/strict'
import test from 'node:test'
import { loadPractice, savePractice, practiceCacheKey } from './practiceStorage.js'


test('practice restores answers/index, isolates topics and imports legacy questions as exclusions only', (t) => {
  const values = new Map()
  const original = Object.getOwnPropertyDescriptor(globalThis, 'localStorage')
  Object.defineProperty(globalThis, 'localStorage', { configurable: true,
    value: { getItem: (key) => values.get(key), setItem: (key, value) => values.set(key, value) } })
  t.after(() => {
    if (original) Object.defineProperty(globalThis, 'localStorage', original)
    else delete globalThis.localStorage
  })
  const key = practiceCacheKey('doc', { id: 'topic' })
  const question = { id: 'q1', question: 'How does this operation work?', sources: [{ page: 1 }],
    options: ['A', 'B', 'C', 'D'].map((key) => ({ key, text: key, isCorrect: key === 'A' })) }
  savePractice(key, { questions: [question], answers: { q1: 'B', missing: 'A' }, index: 99 })
  assert.deepEqual(loadPractice(key).answers, { q1: 'B' })
  assert.equal(loadPractice(key).index, 0)
  assert.deepEqual(loadPractice(practiceCacheKey('doc', { id: 'another' })), { excluded: [] })
  values.delete(key)
  values.set(key.replace('_rolling_v3', '_sources_v2'), JSON.stringify([question]))
  assert.deepEqual(loadPractice(key), { excluded: [question] })
})
