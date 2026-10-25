import assert from 'node:assert/strict'
import test from 'node:test'
import { buildQuizVerification } from './quizVerification.js'

test('quiz verification includes the selected answer, all options, explanation and original source IDs', () => {
  const scope = { id: 'binary', title: 'Binary search', documentId: 'doc' }
  const request = buildQuizVerification({ id: 'q1', question: 'Which input?', explanation: 'It must be sorted.',
    options: [{ key: 'A', text: 'Sorted', isCorrect: true }, { key: 'B', text: 'Unsorted' }],
    sources: [{ knowledge_base_id: 'private', document_id: 'doc', citation_id: 'source-1' }] }, scope)
  assert.equal(request.knowledge_base_id, 'private')
  assert.equal(request.target.artifact, 'mcq')
  assert.match(request.target.answer, /Selected answer: A: Sorted/)
  assert.match(request.target.answer, /B: Unsorted/)
  assert.match(request.target.answer, /Explanation: It must be sorted/)
  assert.deepEqual(request.target.document_ids, ['doc'])
  assert.deepEqual(request.target.source_ids, ['source-1'])
  assert.deepEqual(request.target.scope, scope)
})
