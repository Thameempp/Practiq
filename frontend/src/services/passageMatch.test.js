import assert from 'node:assert/strict'
import test from 'node:test'
import { matchPassage } from './passageMatch.js'

test('exact source quotes match across PDF.js spans, line breaks, hyphenation and ligatures', () => {
  const parts = ['Photo-', 'synthesis converts light into ', 'chemical energy stored in sugars.']
  const match = matchPassage(parts, 'Photosynthesis converts light into chemical energy stored in sugars.', [0])
  assert.deepEqual(match.start, { index: 0, offset: 0, end: 1 })
  assert.equal(match.end.index, 2)
  assert.equal(match.end.end, parts[2].length)
  assert.equal(matchPassage(parts, 'Photosynthesis converts light into chemical energy stored in sugars.'), null)
  assert.ok(matchPassage(parts, 'Photo- synthesis converts light into chemical energy stored in sugars.'))
  assert.ok(matchPassage(['The ofﬁce contains a detailed scientific diagram.'], 'The office contains a detailed scientific diagram.'))
})

test('repeated, short, scanned or absent passages never produce speculative highlights', () => {
  const quote = 'Binary search repeatedly halves a sorted search range.'
  assert.equal(matchPassage([quote, quote], quote), null)
  assert.equal(matchPassage([], quote), null)
  assert.equal(matchPassage(['Completely unrelated material'], quote), null)
  assert.equal(matchPassage(['A short phrase'], 'short'), null)
})

test('UTF-16 DOM offsets survive astral characters and Unicode normalization', () => {
  const part = '🧠 The learning system tracks scientific evidence carefully.'
  const match = matchPassage([part], 'The learning system tracks scientific evidence carefully.')
  assert.equal(match.start.offset, 3)
  assert.equal(match.end.end, part.length)
})

test('minus signs and meaningful internal hyphens cannot be normalized into different facts', () => {
  assert.equal(matchPassage(['The voltage of the node is 20 volts under the load.'],
    'The voltage of the node is -20 volts under the load.'), null)
  assert.equal(matchPassage(['This is a stateoftheart scientific measurement device.'],
    'This is a state-of-the-art scientific measurement device.'), null)
})
