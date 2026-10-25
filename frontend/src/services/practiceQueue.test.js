import assert from 'node:assert/strict'
import test from 'node:test'
import { createPracticeQueue } from './practiceQueue.js'

const question = (index) => ({ id: `q${index}`, question: `Describe concept ${index}?`,
  options: [{ key: 'A', text: `Answer ${index}`, isCorrect: true }], sources: [{ page: 1 }] })
const tick = () => new Promise((resolve) => setImmediate(resolve))


test('answering 1 and 2 creates 6 and 7 sequentially without replacing existing questions', async () => {
  const releases = [], counts = []
  let state
  const queue = createPracticeQueue({ questions: Array.from({ length: 5 }, (_, i) => question(i + 1)) },
    async (count) => { counts.push(count); return new Promise((resolve) => releases.push(resolve)) },
    (next) => { state = next })
  queue.start()
  queue.answer('q1', 'A')
  queue.answer('q1', 'A')
  queue.answer('q2', 'A')
  assert.deepEqual(counts, [1])
  assert.equal(state.questions.length, 5)
  releases.shift()([question(6)])
  await tick()
  assert.deepEqual(counts, [1, 1])
  releases.shift()([question(7)])
  await tick()
  assert.deepEqual(state.questions.map((q) => q.id), ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7'])
  assert.equal(Object.keys(state.answers).length, 2)
  queue.stop()
})


test('late generation after topic disposal never publishes or appends', async () => {
  let release, state
  const queue = createPracticeQueue({}, () => new Promise((resolve) => { release = resolve }),
    (next) => { state = next })
  queue.start()
  const before = state
  queue.stop()
  release([question(1)])
  await tick()
  assert.equal(state, before)
})


test('background failure preserves answers and questions; a later answer can resume refill', async () => {
  let state, calls = 0
  const queue = createPracticeQueue({ questions: Array.from({ length: 5 }, (_, i) => question(i + 1)) },
    async () => { if (++calls === 1) throw new Error('Temporarily unavailable'); return [question(calls + 4)] },
    (next) => { state = next })
  queue.start(); queue.answer('q1', 'A')
  await tick()
  assert.equal(state.questions.length, 5)
  assert.equal(state.answers.q1, 'A')
  assert.match(state.backgroundError, /unavailable/)
  queue.answer('q2', 'A')
  await tick()
  assert.equal(state.questions.length, 7)
  queue.stop()
})


test('restored answers refill only missing questions and retain navigation', async () => {
  let state, calls = 0
  const initial = { questions: Array.from({ length: 5 }, (_, i) => question(i + 1)),
    answers: { q1: 'A', q2: 'A' }, index: 2 }
  const queue = createPracticeQueue(initial, async (count) => {
    assert.equal(count, 1)
    return [question(6 + calls++)]
  }, (next) => { state = next })
  queue.start()
  await tick()
  assert.equal(calls, 2)
  assert.equal(state.index, 2)
  assert.equal(state.questions.length, 7)
  queue.stop()
})


test('a repeated stem with a new ID cannot enter the queue', async () => {
  let state
  const initial = { questions: Array.from({ length: 5 }, (_, i) => question(i + 1)) }
  const queue = createPracticeQueue(initial, async () => [{ ...question(1), id: 'new-id' }],
    (next) => { state = next })
  queue.start(); queue.answer('q1', 'A')
  await tick()
  assert.equal(state.questions.length, 5)
  assert.match(state.backgroundError, /distinct/)
  assert.equal(state.pending, false)
  queue.stop()
})
