import assert from 'node:assert/strict'
import test from 'node:test'
import React from 'react'
import ReactMarkdown from 'react-markdown'
import { renderToStaticMarkup } from 'react-dom/server'
import { normalizeMarkdown, markdownPlugins, mathPlugins } from './markdownContent.js'

const id = 'c' + 'a'.repeat(24)
const sources = { [id]: { id, document_id: 'doc', filename: 'Notes.pdf', page: 2 } }
const render = (content) => renderToStaticMarkup(React.createElement(ReactMarkdown,
  { remarkPlugins: markdownPlugins, rehypePlugins: mathPlugins }, normalizeMarkdown(content, sources)))

test('inline and display TeX render fractions, subscripts, units and accessible MathML', () => {
  const html = render(String.raw`**Inductance**: \(V_L = L\frac{dI}{dt}\).

\[
L = \frac{\mu N^{2}\pi R^{2}}{l}
\]`)
  assert.match(html, /<strong>Inductance<\/strong>/)
  assert.match(html, /class="katex-display"/)
  assert.match(html, /class="katex"/)
  assert.match(html, /<math[^>]*xmlns=/)
  assert.match(html, /<mfrac>/)
  assert.doesNotMatch(html, /katex-error/)
})

test('dollar math also renders while fenced and inline code remain literal', () => {
  assert.match(render('$x^2$\n\n$$\ny = 2x\n$$'), /katex-display/)
  const code = String.raw`Use \(x\), keep \`literal\``
  const fenced = '```tex\n' + String.raw`\[x\] 【${id}】` + '\n```'
  assert.equal(normalizeMarkdown(fenced, sources), fenced)
  const inline = '`' + String.raw`\(x\) 【${id}】` + '`'
  assert.equal(normalizeMarkdown(inline, sources), inline)
  assert.equal(normalizeMarkdown('~~~tex\n' + code + '\n~~~'), '~~~tex\n' + code + '\n~~~')
})

test('raw known sources become short links; unknown IDs never become clickable', () => {
  assert.equal(normalizeMarkdown(`Claim 【${id}】 and [[${id}]].`, sources),
    `Claim [1](#source-${id}) and [1](#source-${id}).`)
  assert.equal(normalizeMarkdown('Claim 【c' + 'b'.repeat(24) + '】', sources), 'Claim (source unavailable)')
  assert.equal(normalizeMarkdown(`Claim 【${id.slice(0, 12)}`, sources), 'Claim ')
})

test('Unicode PDF spacing in equations renders without KaTeX warnings while prose and code stay literal', (t) => {
  const warnings = t.mock.method(console, 'warn', () => {})
  const math = String.raw`$R = 10 \mathrm{k}\Omega, \text{value in kiloohms}$` + '\n\n$$\n' + 'V = 2 I\n$$'
  const html = render(math)
  assert.doesNotMatch(html, /katex-error/)
  assert.match(html, /katex-display/)
  assert.equal(warnings.mock.callCount(), 0)
  assert.equal(normalizeMarkdown('A B and `A B`'), 'A B and `A B`')
  assert.match(render('A B and `A B`'), /A B and <code>A B<\/code>/)
  assert.match(render('```text\nA B\n```'), /A B/)
})
