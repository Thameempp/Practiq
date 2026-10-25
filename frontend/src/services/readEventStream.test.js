import assert from 'node:assert/strict'
import test from 'node:test'
import { readEventStream } from './readEventStream.js'

function response(content, size = 1) {
  const bytes = new TextEncoder().encode(content)
  return new Response(new ReadableStream({ start(controller) {
    for (let index = 0; index < bytes.length; index += size) controller.enqueue(bytes.slice(index, index + size))
    controller.close()
  } }))
}

test('fragmented SSE separates page progress from answer text and handles UTF-8', async () => {
  const source = 'event: progress\ndata: {"label":"Pages 1–269","stage":"reading"}\n\n'
    + ': keep-alive\n\nevent: text\ndata: "First 🧠"\n\nevent: text\ndata: " second"\n\n'
    + 'event: done\ndata: null\n\n'
  const updates = [], progress = []
  const result = await readEventStream(response(source), (text) => updates.push(text),
    (value) => progress.push(value), new AbortController().signal)
  assert.equal(result, 'First 🧠 second')
  assert.equal(updates[0], 'First 🧠')
  assert.equal(progress[0].label, 'Pages 1–269')
  assert.ok(!result.includes('Pages'))
})

test('a provider failure is an error, never a successful answer or hidden completion', async () => {
  const updates = []
  await assert.rejects(readEventStream(response('event: text\ndata: "Partial"\n\n'
    + 'event: error\ndata: "Provider quota exhausted"\n\n'), (text) => updates.push(text),
  null, new AbortController().signal), /Provider quota exhausted/)
  assert.deepEqual(updates, ['Partial'])
})

test('truncated event streams fail instead of marking partial summaries complete', async () => {
  await assert.rejects(readEventStream(response('event: text\ndata: "Partial"\n\n'), () => {},
    null, new AbortController().signal), /interrupted/)
})

test('source and citation events survive byte fragmentation and precede linked text', async () => {
  const events = []
  const source = 'event: sources\ndata: [{"id":"c1","filename":"科学.pdf","page":4}]\n\n'
    + 'event: citation\ndata: {"id":"c1","label":"1"}\n\n'
    + 'event: text\ndata: "Claim [1]"\n\nevent: done\ndata: null\n\n'
  await readEventStream(response(source), (text) => events.push(['text', text]), null,
    new AbortController().signal, (kind, data) => events.push([kind, data]))
  assert.deepEqual(events.map(([kind]) => kind), ['sources', 'citation', 'text'])
  assert.equal(events[0][1][0].filename, '科学.pdf')
})

test('abort interrupts pending SSE reads without delivering stale progress or text', async () => {
  const controller = new AbortController()
  const stream = new ReadableStream()
  const reading = readEventStream(new Response(stream), () => assert.fail('stale text'),
    () => assert.fail('stale progress'), controller.signal)
  controller.abort()
  assert.equal(await reading, '')
  assert.equal(stream.locked, false)
})

test('aborting within a metadata callback suppresses later frames in the same packet', async () => {
  const controller = new AbortController(), events = []
  const frames = 'event: sources\ndata: []\n\nevent: text\ndata: "stale"\n\nevent: done\ndata: null\n\n'
  await readEventStream(response(frames, 10000), () => assert.fail('stale text'), null,
    controller.signal, (kind) => { events.push(kind); controller.abort() })
  assert.deepEqual(events, ['sources'])
})

test('agent lifecycle metadata reaches the UI independently of answer and progress', async () => {
  const events = []
  const frames = 'event: agent\ndata: {"id":"a1","name":"Retrieval","state":"started"}\n\n'
    + 'event: text\ndata: "Answer"\n\nevent: done\ndata: null\n\n'
  const text = await readEventStream(response(frames), () => {}, null,
    new AbortController().signal, (kind, data) => events.push([kind, data]))
  assert.equal(text, 'Answer')
  assert.deepEqual(events, [['agent', { id: 'a1', name: 'Retrieval', state: 'started' }]])
})
