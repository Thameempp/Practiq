import assert from 'node:assert/strict'
import test from 'node:test'
import { recallQuestion } from './questionHistory.js'

const empty = () => ({ index: -1, draft: '' })
const event = (key, value = '', options = {}) => ({
  key, selectionStart: value.length, selectionEnd: value.length, ...options,
})
const questions = ['First question', 'Second question']

test('arrows browse submitted questions and restore the unsent draft', () => {
  let state = recallQuestion(questions, 'Draft', event('ArrowUp', 'Draft'), empty())
  assert.equal(state.value, 'Second question')
  state = recallQuestion(questions, state.value, event('ArrowUp', state.value), state)
  assert.equal(state.value, 'First question')
  state = recallQuestion(questions, state.value, event('ArrowUp', state.value), state)
  assert.equal(state.value, 'First question')
  state = recallQuestion(questions, state.value, event('ArrowDown', state.value), state)
  assert.equal(state.value, 'Second question')
  state = recallQuestion(questions, state.value, event('ArrowDown', state.value), state)
  assert.equal(state.value, 'Draft')
  assert.equal(recallQuestion(questions, state.value, event('ArrowDown', state.value), state), null)
})

test('multiline drafts preserve native movement except at the first or last line', () => {
  const value = 'First line\nSecond line'
  assert.equal(recallQuestion(questions, value, event('ArrowUp', value), empty()), null)
  const state = recallQuestion(questions, value, event('ArrowUp', value, {
    selectionStart: 3, selectionEnd: 3,
  }), empty())
  assert.equal(state.value, 'Second question')
  assert.equal(recallQuestion(questions, value, event('ArrowDown', value, {
    selectionStart: 3, selectionEnd: 3,
  }), state), null)
  assert.equal(recallQuestion(questions, state.value, event('ArrowDown', state.value), state).value, value)
})

test('empty history, selections, modifiers and IME input are left alone', () => {
  assert.equal(recallQuestion([], '', event('ArrowUp'), empty()), null)
  for (const options of [{ shiftKey: true }, { altKey: true }, { ctrlKey: true },
    { metaKey: true }, { isComposing: true }, { keyCode: 229 },
    { selectionStart: 0, selectionEnd: 1 }]) {
    assert.equal(recallQuestion(questions, 'x', event('ArrowUp', 'x', options), empty()), null)
  }
  assert.equal(recallQuestion(questions, '', event('Enter'), empty()), null)
})
