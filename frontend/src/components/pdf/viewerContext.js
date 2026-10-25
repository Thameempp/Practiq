import { createContext, useContext } from 'react'

export const PdfViewerContext = createContext(null)


export const usePdfViewer = () => useContext(PdfViewerContext)
