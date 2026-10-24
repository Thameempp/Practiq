import { readFileSync, readdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { createRequire } from 'node:module'

// Serve PDF.js fonts, character maps and image decoders locally, including offline builds.
export function pdfAssets() {
  const require = createRequire(import.meta.url)
  const root = dirname(require.resolve('pdfjs-dist/package.json'))
  const files = new Map()
  files.set('/pdf-assets/LICENSE', join(root, 'LICENSE'))
  for (const folder of ['cmaps', 'standard_fonts', 'wasm', 'iccs']) {
    for (const name of readdirSync(join(root, folder))) {
      files.set(`/pdf-assets/${folder}/${name}`, join(root, folder, name))
    }
  }
  return {
    name: 'local-pdf-assets',
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        const path = files.get(request.url?.split('?')[0])
        if (!path) return next()
        response.setHeader('Content-Type', path.endsWith('.wasm') ? 'application/wasm'
          : path.endsWith('.js') ? 'text/javascript' : 'application/octet-stream')
        response.end(readFileSync(path))
      })
    },
    generateBundle() {
      for (const [url, path] of files) {
        this.emitFile({ type: 'asset', fileName: url.slice(1), source: readFileSync(path) })
      }
    },
  }
}
