import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import 'lenis/dist/lenis.css'
import App from './App.jsx'
import { PdfViewerProvider } from './components/pdf/PdfViewerContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <PdfViewerProvider><App /></PdfViewerProvider>
  </StrictMode>,
)
