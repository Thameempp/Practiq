import assert from 'node:assert/strict'
import test from 'node:test'
import { streamRequest } from './streamRequest.js'

test('clarification JSON is delivered as text plus document choices', async (t) => {
  const route = { status: 'clarification_required', message: 'Choose a PDF', documents: [{ document_id: 'a' }] }
  t.mock.method(globalThis, 'fetch', async () => Response.json(route))
  const updates = [], routes = []
  const result = await streamRequest({ url: '/ask', body: {}, signal: new AbortController().signal,
    onText: (text) => updates.push(text), onRoute: (value) => routes.push(value) })
  assert.equal(result, 'Choose a PDF')
  assert.deepEqual(updates, ['Choose a PDF'])
  assert.deepEqual(routes, [route])
})

test('plain-text responses deliver intermediate content and retain the final text', async (t) => {
  const stream = new ReadableStream({ start(controller) {
    controller.enqueue(new TextEncoder().encode('First '))
    controller.enqueue(new TextEncoder().encode('second'))
    controller.close()
  } })
  t.mock.method(globalThis, 'fetch', async () => new Response(stream))
  const updates = []
  const result = await streamRequest({ url: '/ask', body: {}, signal: new AbortController().signal,
    onText: (text) => updates.push(text) })
  assert.equal(updates[0], 'First ')
  assert.equal(result, 'First second')
})

test('late responses from an aborted request cannot deliver text or clarification', async (t) => {
  let deliver
  t.mock.method(globalThis, 'fetch', () => new Promise((resolve) => { deliver = resolve }))
  const controller = new AbortController()
  let callbacks = 0
  const request = streamRequest({ url: '/ask', body: {}, signal: controller.signal,
    onText: () => callbacks++, onRoute: () => callbacks++ })
  controller.abort()
  deliver(Response.json({ message: 'Old request' }))
  await assert.rejects(request, { name: 'AbortError' })
  assert.equal(callbacks, 0)
})

test('server errors expose the safe API message without JSON framing', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => Response.json({ detail: 'Service unavailable' }, { status: 503 }))
  await assert.rejects(streamRequest({ url: '/ask', body: {}, signal: new AbortController().signal,
    onText: () => assert.fail('Must not emit error content as an answer') }), { message: 'Service unavailable' })
})
