import assert from 'node:assert/strict'
import test from 'node:test'
import { buildQuestionRequest } from './questionRequest.js'

const documents = [{ documentId: 'first' }, { documentId: 'last' }]

test('general chat searches the full knowledge base without selecting the latest upload', () => {
  const request = buildQuestionRequest({ question: 'Explain energy', documents, conversationId: 'chat' })
  assert.equal(request.document_id, null)
  assert.equal(request.scope, null)
  assert.deepEqual(request.document_order, ['first', 'last'])
  assert.equal(request.conversation_id, 'chat')
})

test('an outline selection explicitly restricts the question to its PDF', () => {
  const scope = { title: 'Energy', documentId: 'first', page: 7 }
  const request = buildQuestionRequest({ question: 'Explain', documents, scope })
  assert.equal(request.document_id, 'first')
  assert.deepEqual(request.scope, scope)
})

test('clarification choice is preserved without adding an active document restriction', () => {
  const request = buildQuestionRequest({ question: 'Physics.pdf', documents, selectionId: 'first' })
  assert.equal(request.selection_id, 'first')
  assert.equal(request.document_id, null)
})
