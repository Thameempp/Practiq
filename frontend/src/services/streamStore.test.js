import assert from 'node:assert/strict'
import test from 'node:test'
import { createStreamStore } from './streamStore.js'

function fixture() {
  const jobs = new Map()
  let id = 0
  const store = createStreamStore({
    schedule(callback, delay) { assert.equal(delay, 35); jobs.set(++id, callback); return id },
    cancel(timer) { jobs.delete(timer) },
  })
  return { store, jobs, tick() { for (const callback of [...jobs.values()]) callback() } }
}

test('first text appears immediately; a burst updates subscribers only once per batch', () => {
  const { store, jobs, tick } = fixture()
  const updates = []
  store.subscribe(() => updates.push(store.getText()))
  store.update('A')
  assert.deepEqual(updates, ['A'])
  for (let count = 2; count <= 100; count++) store.update('A'.repeat(count))
  assert.equal(jobs.size, 1)
  assert.equal(updates.length, 1)
  tick()
  assert.equal(updates.length, 2)
  assert.equal(store.getText().length, 100)
})

test('completion/stop flushes the last pending chunk immediately and clears timers', () => {
  const { store, jobs } = fixture()
  store.update('First')
  store.update('First final')
  store.finish()
  assert.equal(store.getText(), 'First final')
  assert.equal(jobs.size, 0)
})

test('reset and disposal discard pending content from the previous response', () => {
  const { store, tick } = fixture()
  store.update('Old')
  store.update('Old pending')
  store.reset()
  store.update('New')
  tick()
  assert.equal(store.getText(), 'New')
  store.update('New pending')
  store.discard()
  tick()
  assert.equal(store.getText(), 'New')
})

test('snapshot identity stays stable between flushes for React external-store subscriptions', () => {
  const { store } = fixture()
  store.update('Text')
  const snapshot = store.getSnapshot()
  store.update('Text waiting')
  assert.equal(store.getSnapshot(), snapshot)
  store.finish()
  assert.notEqual(store.getSnapshot(), snapshot)
})

test('nested and concurrent agent activity stays separate from text and clears on finish/reset', () => {
  const { store } = fixture()
  const agent = (id, name, state) => store.metadata('agent', { id, name, state })
  agent('verify', 'Answer Verifier', 'started')
  agent('search1', 'Retrieval', 'started')
  agent('search2', 'Retrieval', 'started')
  agent('search1', 'Retrieval', 'finished')
  assert.deepEqual(store.getSnapshot().agents.map(({ id }) => id), ['verify', 'search2'])
  agent('search2', 'Retrieval', 'finished')
  assert.equal(store.getSnapshot().agents.at(-1).name, 'Answer Verifier')
  assert.equal(store.getText(), '')
  assert.deepEqual(store.getSnapshot().citations, {})
  store.finish()
  assert.deepEqual(store.getSnapshot().agents, [])
  agent('old', 'Retrieval', 'started')
  store.reset()
  assert.deepEqual(store.getSnapshot().agents, [])
})
