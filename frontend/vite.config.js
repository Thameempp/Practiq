import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { pdfAssets } from './pdfAssets.js'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), pdfAssets()],
  optimizeDeps: { include: ['pdfjs-dist'] },
})
