import assert from 'node:assert/strict'
import test from 'node:test'
import { deletePdfs } from './documentsApi.js'

test('bulk deletion reports successful removals and preserves failed documents', async (t) => {
  const documents = [{ documentId: 'first' }, { documentId: 'failed' }, { documentId: 'last' }]
  t.mock.method(globalThis, 'fetch', async (url) => {
    if (url.endsWith('/failed')) return Response.json({ detail: 'Document is busy.' }, { status: 409 })
    return new Response(null, { status: 204 })
  })
  const result = await deletePdfs('/api', documents)
  assert.deepEqual(result.removed, [documents[0], documents[2]])
  assert.equal(result.errors.length, 1)
  assert.equal(result.errors[0].message, 'Document is busy.')
})
