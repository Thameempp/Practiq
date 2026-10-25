import assert from 'node:assert/strict'
import test from 'node:test'
import { createMarkdownBlocks } from './markdownBlocks.js'

test('completed blocks retain identity while the unfinished block grows', () => {
  const parser = createMarkdownBlocks()
  const first = parser.update('Paragraph.\n\nNext line\n')
  const next = parser.update('Paragraph.\n\nNext line\nmore tokens')
  assert.equal(first.blocks.length, 1)
  assert.equal(next.blocks[0], first.blocks[0])
  assert.equal(next.tail, 'Next line\nmore tokens')
})

test('blank lines inside open code fences do not prematurely render a block', () => {
  const parser = createMarkdownBlocks()
  const code = '```js\nconst x = 1\n\nconsole.log(x)\n'
  assert.equal(parser.update(code).blocks.length, 0)
  const done = parser.update(code + '```\n\nAfter\n')
  assert.equal(done.blocks.length, 1)
  assert.match(done.blocks[0].text, /console.log/)
})

test('loose list items remain one block and tables wait for their boundary', () => {
  const parser = createMarkdownBlocks()
  const list = '1. First\n\n2. Second\n\n'
  assert.equal(parser.update(list).blocks.length, 0)
  const table = '| A | B |\n|---|---|\n| 1 | 2 |\n'
  let result = parser.update(list + table)
  assert.equal(result.blocks.length, 1)
  assert.equal(result.tail, table)
  result = parser.update(list + table + '\nAfter\n')
  assert.equal(result.blocks.length, 2)
})

test('display math stays unfinished until its closing delimiter and new content resets parsing', () => {
  const parser = createMarkdownBlocks()
  assert.equal(parser.update('$$\nx = y\n\n').blocks.length, 0)
  assert.equal(parser.update('$$\nx = y\n\n$$\n\nAfter\n').blocks.length, 1)
  const reset = parser.update('Replacement')
  assert.deepEqual(reset.blocks, [])
  assert.equal(reset.tail, 'Replacement')
})

test('every character survives incremental UTF-8/line-boundary delivery', () => {
  const parser = createMarkdownBlocks()
  const content = 'First 🧠\n\n~~~py\nline\n\n~~~\n\nLast'
  let result
  for (let index = 1; index <= content.length; index++) result = parser.update(content.slice(0, index))
  assert.equal(result.blocks.map((block) => block.text).join('') + result.tail, content)
})
