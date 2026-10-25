import { citationMetadata } from './citationMetadata.js'

const KEY = 'practiq_chat_v1'
const TTL = 24 * 60 * 60 * 1000


export function compactMessages(messages) {
  const kept = []
  let size = 0
  for (let index = messages.length - 1; index > 0; index -= 2) {
    const user = messages[index - 1], answer = messages[index]
    if (user?.role !== 'user' || answer?.role !== 'assistant'
      || typeof user.content !== 'string' || typeof answer.content !== 'string'
      || typeof user.id !== 'string' || typeof answer.id !== 'string' || !user.id || !answer.id) continue
    if (!answer.content) continue // Do not restore an in-flight request after a reload.
    const pair = [user, answer].map((message) => ({
      id: message.id, role: message.role, content: message.content,
      ...(message.sources ? citationMetadata(message) : {}),
      ...(typeof message.scope?.title === 'string' ? { scope: {
        title: message.scope.title, pageLabel: String(message.scope.pageLabel || ''),
      } } : {}),
      ...(Array.isArray(message.documentChoices) ? { documentChoices: message.documentChoices.filter(
        (doc) => typeof doc?.document_id === 'string' && typeof doc?.filename === 'string',
      ).slice(0, 200) } : {}),
    }))
    size += JSON.stringify(pair).length
    if (size > 60000 || kept.length >= 40) break
    kept.unshift(...pair)
  }
  return kept
}


export function readChatSession(storage, now = Date.now()) {
  try {
    const value = JSON.parse((storage ?? sessionStorage).getItem(KEY))
    if (typeof value?.id === 'string' && value.id.length > 0 && value.id.length <= 100
      && Number.isFinite(value.updatedAt) && now - value.updatedAt < TTL && Array.isArray(value.messages)) {
      return { id: value.id, messages: compactMessages(value.messages) }
    }
  } catch { /* Chat still works when browser storage is unavailable. */ }
  return { id: crypto.randomUUID(), messages: [] }
}


export function saveChatSession(id, messages, storage) {
  try { (storage ?? sessionStorage).setItem(KEY, JSON.stringify({ id, messages: compactMessages(messages), updatedAt: Date.now() })) }
  catch { /* Browser persistence is optional. Server-side context remains bounded. */ }
}
