import assert from 'node:assert/strict'
import test from 'node:test'
import { requestPractice } from './practiceApi.js'


test('refill requests one question and limits exclusion payloads to the latest hundred', async (t) => {
  const questions = [{ id: 'unique', question: 'Which operation preserves order?',
    options: ['A', 'B', 'C', 'D'].map((key) => ({ key })), sources: [{ page: 1 }] }]
  const fetch = t.mock.method(globalThis, 'fetch', async () => Response.json({ questions }))
  const previous = Array.from({ length: 120 }, (_, index) => ({ question: `Past question ${index}` }))
  const result = await requestPractice('doc', { id: 'topic' }, 1, previous, new AbortController().signal)
  const body = JSON.parse(fetch.mock.calls[0].arguments[1].body)
  assert.equal(body.count, 1)
  assert.equal(body.exclude_questions.length, 100)
  assert.equal(body.exclude_questions[0], 'Past question 20')
  assert.deepEqual(result, questions)
})


test('cancellation during quota backoff prevents another request', async (t) => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => Response.json({ detail: 'Rate limited' },
    { status: 429, headers: { 'retry-after': '30' } }))
  const controller = new AbortController()
  const request = requestPractice('doc', null, 1, [], controller.signal)
  setImmediate(() => controller.abort())
  await assert.rejects(request, { name: 'AbortError' })
  assert.equal(fetch.mock.callCount(), 1)
})
