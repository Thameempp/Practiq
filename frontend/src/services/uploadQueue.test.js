import assert from 'node:assert/strict'
import test from 'node:test'
import { createUploadQueue } from './uploadQueue.js'
import { uploadPdfFile, deletePdf } from './documentsApi.js'

test('multiple upload batches never overlap and a failed file does not block later files', async () => {
  const starts = [], finishes = [], release = []
  let active = 0, peak = 0
  const enqueue = createUploadQueue(async (file) => {
    starts.push(file); active++; peak = Math.max(peak, active)
    await new Promise((resolve) => release.push(resolve))
    active--; finishes.push(file)
    if (file === 'bad.pdf') throw new Error('Rejected')
    return file
  })
  const first = enqueue('first.pdf'), bad = enqueue('bad.pdf').catch((error) => error.message)
  const last = enqueue('last.pdf')
  await Promise.resolve()
  assert.deepEqual(starts, ['first.pdf'])
  release.shift()(); assert.equal(await first, 'first.pdf')
  await Promise.resolve()
  release.shift()(); assert.equal(await bad, 'Rejected')
  await Promise.resolve()
  release.shift()(); assert.equal(await last, 'last.pdf')
  assert.equal(peak, 1)
  assert.deepEqual(finishes, ['first.pdf', 'bad.pdf', 'last.pdf'])
})

test('document API validates files before sending and preserves upload identity/hierarchy', async (t) => {
  const request = t.mock.method(globalThis, 'fetch', async () => Response.json({
    document_id: 'doc', filename: 'Notes.pdf', pages: 2, chunks_count: 3, hierarchy: [{ id: 'topic' }],
  }))
  await assert.rejects(uploadPdfFile('/api', { name: 'wrong.txt', type: 'text/plain' }), /valid PDF/)
  assert.equal(request.mock.callCount(), 0)
  const file = new Blob(['pdf'], { type: 'application/pdf' }); file.name = 'Notes.pdf'
  const result = await uploadPdfFile('/api', file)
  assert.equal(result.documentId, 'doc')
  assert.deepEqual(result.hierarchy, [{ id: 'topic' }])
  assert.equal(request.mock.calls[0].arguments[1].body.get('knowledge_base_id'), 'local')
})

test('server document errors are displayed as messages rather than raw JSON', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => Response.json({ detail: 'PDF is still processing.' }, { status: 409 }))
  await assert.rejects(deletePdf('/api', { documentId: 'doc', fileName: 'Notes.pdf' }), /still processing/)
  await assert.rejects(deletePdf('/api', {}), /no backend ID/)
})
