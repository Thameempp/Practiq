export function DocumentChoices({ documents, disabled, onSelect }) {
  if (!documents?.length) return null
  return (
    <div className="document-choices" role="group" aria-label="Choose a PDF">
      {documents.map((doc, index) => (
        <button key={doc.document_id} type="button" className="document-choice"
          disabled={disabled || doc.status !== 'ready'}
          onClick={() => onSelect(doc.document_id, doc.filename)}>
          <span>{index + 1}. {doc.filename}</span>
          {doc.status !== 'ready' && <small>{doc.status === 'processing' ? 'Indexing…' : 'Upload failed'}</small>}
        </button>
      ))}
    </div>
  )
}
