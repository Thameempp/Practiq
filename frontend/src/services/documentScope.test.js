import assert from 'node:assert/strict'
import test from 'node:test'
import { buildScopePayload, outlineTitles } from './documentScope.js'

test('scope payload retains document identity and nested topics with a bounded size', () => {
  const node = { id: 'parent', documentId: 'doc', title: 'Collections', page: 2,
    children: Array.from({ length: 100 }, (_, i) => ({ title: `Topic ${i}` })) }
  const scope = buildScopePayload(node)
  assert.equal(scope.documentId, 'doc')
  assert.equal(scope.id, 'parent')
  assert.equal(scope.pageLabel, 'p. 2')
  assert.equal(scope.descendantTitles.length, 30)
  assert.equal(scope.descendantTitles.at(-1), 'Topic 29')
})

test('outline hints exclude other PDFs and respect the existing title limit', () => {
  const hierarchy = Array.from({ length: 100 }, (_, i) => ({ documentId: 'doc', title: `Chapter ${i}` }))
  hierarchy.push({ documentId: 'other', title: 'Other PDF' })
  assert.equal(outlineTitles(hierarchy, 'doc').length, 60)
  assert.equal(outlineTitles(hierarchy, 'doc').includes('Other PDF'), false)
})
