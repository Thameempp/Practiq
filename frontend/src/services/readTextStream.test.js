import assert from 'node:assert/strict'
import test from 'node:test'
import { readTextStream } from './readTextStream.js'

test('decodes a source page marker split across UTF-8 stream chunks', async () => {
  const bytes = new TextEncoder().encode('PDF pages 2–4')
  const stream = new ReadableStream({ start(controller) {
    controller.enqueue(bytes.slice(0, 12))
    controller.enqueue(bytes.slice(12))
    controller.close()
  } })
  const updates = []
  const result = await readTextStream(new Response(stream), (text) => updates.push(text), new AbortController().signal)
  assert.equal(result, 'PDF pages 2–4')
  assert.equal(updates.at(-1), result)
})

test('does not deliver content from an aborted response', async () => {
  const controller = new AbortController()
  controller.abort()
  const updates = []
  await readTextStream(new Response('Old answer'), (text) => updates.push(text), controller.signal)
  assert.deepEqual(updates, [])
})

test('abort cancels a pending read and releases the stream lock', async () => {
  const controller = new AbortController()
  let cancelled = false
  const stream = new ReadableStream({ cancel() { cancelled = true } })
  const updates = []
  const reading = readTextStream(new Response(stream), (text) => updates.push(text), controller.signal)
  controller.abort()
  await reading
  assert.equal(cancelled, true)
  assert.equal(stream.locked, false)
  assert.deepEqual(updates, [])
})

test('a read failure preserves earlier updates and releases the reader', async () => {
  let reads = 0
  const stream = new ReadableStream({ pull(controller) {
    if (reads++ === 0) controller.enqueue(new TextEncoder().encode('Partial'))
    else controller.error(new Error('Connection interrupted'))
  } })
  const updates = []
  await assert.rejects(readTextStream(new Response(stream), (text) => updates.push(text),
    new AbortController().signal), /Connection interrupted/)
  assert.deepEqual(updates, ['Partial'])
  assert.equal(stream.locked, false)
})
