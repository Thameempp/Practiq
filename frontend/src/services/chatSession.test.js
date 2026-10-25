import assert from 'node:assert/strict'
import test from 'node:test'
import { compactMessages, readChatSession, saveChatSession } from './chatSession.js'

function exchange(index, content = `Answer ${index}`) {
  return [{ id: `u-${index}`, role: 'user', content: `Question ${index}` },
    { id: `a-${index}`, role: 'assistant', content }]
}

function storage() {
  const values = new Map()
  return { getItem: (key) => values.get(key), setItem: (key, value) => values.set(key, value) }
}

test('a reload restores the conversation ID and complete message pairs', () => {
  const saved = storage(), messages = exchange(1)
  saveChatSession('chat-id', messages, saved)
  assert.deepEqual(readChatSession(saved), { id: 'chat-id', messages })
})

test('pending replies are not restored as completed messages', () => {
  const messages = [...exchange(1), ...exchange(2, '')]
  assert.deepEqual(compactMessages(messages), exchange(1))
})

test('message count and size limits discard oldest complete exchanges', () => {
  const messages = Array.from({ length: 50 }, (_, index) => exchange(index)).flat()
  const compact = compactMessages(messages)
  assert.equal(compact.length, 40)
  assert.equal(compact[0].id, 'u-30')
  assert.deepEqual(compactMessages([...exchange(1, 'a'.repeat(40000)), ...exchange(2, 'b'.repeat(40000))]),
    exchange(2, 'b'.repeat(40000)))
})

test('expired, malformed and inaccessible storage starts a fresh chat', () => {
  const saved = storage()
  saved.setItem('practiq_chat_v1', JSON.stringify({ id: 'old', messages: exchange(1), updatedAt: 0 }))
  assert.deepEqual(readChatSession(saved, 86400001).messages, [])
  assert.notEqual(readChatSession(saved, 86400001).id, 'old')
  saved.setItem('practiq_chat_v1', '{invalid')
  assert.deepEqual(readChatSession(saved).messages, [])
  const blocked = { getItem() { throw new Error('Blocked') }, setItem() { throw new Error('Blocked') } }
  assert.doesNotThrow(() => saveChatSession('id', [], blocked))
  assert.deepEqual(readChatSession(blocked).messages, [])
})
