import assert from 'node:assert/strict'
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'
import { createServer } from 'vite'
import config from '../../vite.config.js'

test('PDF.js is ready before a late viewer import without changing its optimized URL', async () => {
  const cacheDir = await mkdtemp(join(tmpdir(), 'practiq-viewer-'))
  const server = await createServer({ ...config, configFile: false, envFile: false,
    root: fileURLToPath(new URL('../../', import.meta.url)), cacheDir, logLevel: 'silent',
    // Simulate a lazy dependency that the initial HTML scan does not discover.
    optimizeDeps: { ...config.optimizeDeps, noDiscovery: true },
    server: { middlewareMode: true, hmr: false, watch: null },
  })
  try {
    const client = server.environments.client
    await client.listen(server)
    const optimizer = client.depsOptimizer
    await Promise.all(Object.values(optimizer.metadata.discovered).map((dep) => dep.processing))
    const ready = optimizer.metadata.optimized['pdfjs-dist']
    assert.ok(ready, 'PDF.js must be optimized before the first source click')
    const hash = ready.browserHash
    const viewer = await server.transformRequest('/src/components/pdf/PdfViewer.jsx')
    assert.match(viewer.code, /PdfDocumentView/)
    const pdf = await server.transformRequest('/src/components/pdf/pdfClient.js')
    assert.match(pdf.code, /pdfjs-dist|pdfjs_dist/)
    assert.equal(optimizer.metadata.optimized['pdfjs-dist'].browserHash, hash)
  } finally {
    await server.close()
    await rm(cacheDir, { recursive: true, force: true })
  }
})
