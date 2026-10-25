import assert from 'node:assert/strict'
import test from 'node:test'
import { readStoredValue, writeStoredValue } from './browserStorage.js'

test('workspace storage rejects corrupt or wrong-shaped data and tolerates blocked storage', () => {
  for (const text of ['{bad', 'null', '42', '"wrong"', '{}']) {
    assert.deepEqual(readStoredValue('kb', [], { getItem: () => text }), [])
  }
  const blocked = { getItem() { throw Error('Blocked') }, setItem() { throw Error('Blocked') } }
  assert.equal(readStoredValue('pdf', null, blocked), null)
  assert.doesNotThrow(() => writeStoredValue('pdf', { documentId: 'doc' }, blocked))
})

test('workspace values persist and empty values clear their own key', () => {
  const values = new Map(), storage = {
    getItem: (key) => values.get(key), setItem: (key, value) => values.set(key, value), removeItem: (key) => values.delete(key),
  }
  writeStoredValue('kb', [{ documentId: 'doc' }], storage)
  assert.deepEqual(readStoredValue('kb', [], storage), [{ documentId: 'doc' }])
  writeStoredValue('kb', [], storage)
  assert.equal(values.has('kb'), false)
})
