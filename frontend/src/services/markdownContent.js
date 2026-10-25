import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { mapMarkdownProse } from './markdownProse.js'
import { cleanSource } from './citationMetadata.js'
import { normalizeMathWhitespace } from './mathWhitespace.js'

export const markdownPlugins = [remarkGfm, remarkMath]
export const mathPlugins = [normalizeMathWhitespace, [rehypeKatex, { trust: false, maxSize: 10, maxExpand: 1000 }]]


export function sourceLabel(id, sources, citations = {}) {
  return citations[id]?.label || String(Object.keys(sources).indexOf(id) + 1)
}


export function normalizeMarkdown(text, sources = {}, citations = {}) {
  return mapMarkdownProse(text, (prose) => prose
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/\\\[([\s\S]*?)\\\]/g, (_, math) => '\n\n$$\n' + math.trim() + '\n$$\n\n')
    .replace(/\\\(([^\n]*?)\\\)/g, (_, math) => '$' + math.trim() + '$')
    .replace(/【(c[0-9a-f]{24})】|\[\[(c[0-9a-f]{24})\]\]/g, (_, fullWidth, square) => {
      const id = fullWidth || square
      return cleanSource(sources[id]) ? `[${sourceLabel(id, sources, citations)}](#source-${id})` : '(source unavailable)'
    })
    .replace(/(?:【|\[\[)c[0-9a-f]{0,24}$/, ''))
}
