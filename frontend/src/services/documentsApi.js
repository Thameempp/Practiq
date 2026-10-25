export async function uploadPdfFile(apiUrl, file, signal) {
  if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
    throw new Error('Please select a valid PDF file.')
  }
  const body = new FormData()
  body.append('file', file)
  body.append('knowledge_base_id', 'local')
  const response = await fetch(`${apiUrl}/upload/upload-pdf/`, { method: 'POST', body, signal })
  const result = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(result.detail || `Upload failed: ${response.status}`)
  }
  return {
    documentId: result.document_id,
    status: 'ready',
    title: file.name.replace(/\.[^/.]+$/, ''),
    fileName: result.filename || file.name,
    pages: result.pages || 0,
    chunks: result.chunks_count || 0,
    hierarchy: result.hierarchy || [],
  }
}


export async function deletePdf(apiUrl, pdf) {
  if (!pdf.documentId) throw new Error('This document has no backend ID and cannot be removed.')
  const response = await fetch(`${apiUrl}/upload/${encodeURIComponent(pdf.documentId)}`, { method: 'DELETE' })
  if (!response.ok) {
    const result = await response.json().catch(() => ({}))
    throw new Error(result.detail || `Could not remove ${pdf.fileName}.`)
  }
}


export async function deletePdfs(apiUrl, documents) {
  const results = await Promise.allSettled(documents.map((pdf) => deletePdf(apiUrl, pdf)))
  return {
    removed: documents.filter((_, index) => results[index].status === 'fulfilled'),
    errors: results.filter((result) => result.status === 'rejected').map((result) => result.reason),
  }
}
