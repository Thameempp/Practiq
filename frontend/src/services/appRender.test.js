import assert from 'node:assert/strict'
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { createServer } from 'vite'
import config from '../../vite.config.js'

test('the restructured application renders the restored workspace and compact composer', async () => {
  const cacheDir = await mkdtemp(join(tmpdir(), 'practiq-render-'))
  const previous = Object.getOwnPropertyDescriptor(globalThis, 'localStorage')
  const doc = { documentId: 'doc', fileName: 'Notes.pdf', title: 'Notes', pages: 2, chunks: 2 }
  const values = { practiq_pdf: doc, practiq_knowledge_base: [doc], practiq_hierarchy: [] }
  Object.defineProperty(globalThis, 'localStorage', { configurable: true, value: {
    getItem: (key) => key in values ? JSON.stringify(values[key]) : null,
  } })
  const server = await createServer({ ...config, configFile: false, envFile: false,
    root: fileURLToPath(new URL('../../', import.meta.url)), cacheDir, logLevel: 'silent',
    server: { middlewareMode: true, hmr: false, watch: null },
  })
  try {
    const { default: App } = await server.ssrLoadModule('/src/App.jsx')
    const html = renderToStaticMarkup(React.createElement(App))
    assert.match(html, /aria-label="Question"/)
    assert.match(html, /send-button composer-action is-empty/)
    assert.match(html, /Notes[.]pdf/)
  } finally {
    await server.close()
    await rm(cacheDir, { recursive: true, force: true })
    if (previous) Object.defineProperty(globalThis, 'localStorage', previous)
    else delete globalThis.localStorage
  }
})
