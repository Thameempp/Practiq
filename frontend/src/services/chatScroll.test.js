import assert from 'node:assert/strict'
import test from 'node:test'
import { observeChatScroll } from './chatScroll.js'

test('manual scrolling pauses streaming follow; reaching the bottom resumes it; cleanup detaches listeners', () => {
  const element = Object.assign(new EventTarget(), { scrollTop: 800, scrollHeight: 1000, clientHeight: 200 })
  const state = { paused: false, programmatic: false, lastTop: 800, touchY: null }
  const updates = [], close = observeChatScroll(element, state, (update) => updates.push(update))
  element.scrollTop = 400
  element.dispatchEvent(new Event('scroll'))
  assert.equal(state.paused, true)
  assert.ok(updates.some((update) => update.showLatest === true))
  element.scrollTop = 800
  element.dispatchEvent(new Event('scroll'))
  assert.equal(state.paused, false)
  assert.equal(updates.at(-1).showLatest, false)
  close()
  const count = updates.length
  element.scrollTop = 0
  element.dispatchEvent(new Event('scroll'))
  assert.equal(updates.length, count)
})

test('programmatic scrolling updates the fade without changing manual follow state', () => {
  const element = Object.assign(new EventTarget(), { scrollTop: 400, scrollHeight: 1000, clientHeight: 200 })
  const state = { paused: false, programmatic: true, lastTop: 800, touchY: null }
  const updates = [], close = observeChatScroll(element, state, (value) => updates.push(value))
  assert.equal(state.paused, false)
  assert.deepEqual(updates, [{ fade: true }])
  close()
})
