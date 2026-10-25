const validId = (id) => typeof id === 'string' && /^c[0-9a-f]{24}$/.test(id)


export function cleanSource(source) {
  if (!validId(source?.id) || typeof source.document_id !== 'string'
    || typeof source.filename !== 'string' || !Number.isInteger(source.page) || source.page < 1) return null
  return { id: source.id, document_id: source.document_id.slice(0, 200),
    filename: source.filename.slice(0, 500), page: source.page,
    page_end: Number.isInteger(source.page_end) ? Math.max(source.page, source.page_end) : source.page,
    knowledge_base_id: String(source.knowledge_base_id || 'local').slice(0, 100),
    quote: typeof source.quote === 'string' ? source.quote.slice(0, 16000) : '' }
}


export function citationMetadata(value = {}) {
  const sources = {}, citations = {}
  for (const candidate of Object.values(value.sources || {}).slice(0, 200)) {
    const source = cleanSource(candidate)
    if (source) sources[source.id] = source
  }
  for (const candidate of Object.values(value.citations || {}).slice(0, 200)) {
    if (sources[candidate?.id] && typeof candidate.label === 'string' && candidate.label.length <= 100) {
      citations[candidate.id] = { id: candidate.id, label: candidate.label }
    }
  }
  return { sources, citations }
}

