import { useCallback, useState } from 'react'

const DEFAULT_WIDTH = 270
const MIN_WIDTH = 200
const MAX_WIDTH = 500


export function KnowledgeBaseSidebar({
  documents = [],
  onRemovePdf,
  onClearAll,
  onUploadClick,
  onUploadFiles,
  isUploading = false,
  scopedNode,
  onClearScope,
  isCollapsed: externalIsCollapsed,
  onToggleCollapse: externalOnToggleCollapse,
}) {
  const [internalCollapsed, setInternalCollapsed] = useState(() => {
    try {
      return localStorage.getItem('practiq_kb_collapsed') === 'true'
    } catch {
      return false
    }
  })

  const isCollapsed = externalIsCollapsed !== undefined ? externalIsCollapsed : internalCollapsed

  const [width, setWidth] = useState(() => {
    try {
      const saved = localStorage.getItem('practiq_kb_width')
      if (saved) {
        const parsed = parseInt(saved, 10)
        if (!isNaN(parsed) && parsed >= MIN_WIDTH && parsed <= MAX_WIDTH) {
          return parsed
        }
      }
    } catch {}
    return DEFAULT_WIDTH
  })

  const [isResizing, setIsResizing] = useState(false)
  const [isNearDivider, setIsNearDivider] = useState(false)
  const [isDragOver, setIsDragOver] = useState(false)


  const handleToggle = useCallback(() => {
    if (externalOnToggleCollapse) {
      externalOnToggleCollapse()
    } else {
      setInternalCollapsed((prev) => {
        const next = !prev
        try {
          localStorage.setItem('practiq_kb_collapsed', String(next))
        } catch {}
        return next
      })
    }
  }, [externalOnToggleCollapse])


  const handleOpen = useCallback(() => {
    if (isCollapsed) {
      handleToggle()
    }
    if (width < MIN_WIDTH) {
      setWidth(DEFAULT_WIDTH)
    }
  }, [isCollapsed, handleToggle, width])


  const handleClose = useCallback(() => {
    if (!isCollapsed) {
      handleToggle()
    }
  }, [isCollapsed, handleToggle])


  // Drag resizer handle on left edge of the right sidebar
  const startResizing = useCallback((startX, startWidth) => {
    setIsResizing(true)
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'

    let currentWidth = startWidth


    const onMove = (moveEvent) => {
      const currentX = moveEvent.touches ? moveEvent.touches[0].clientX : moveEvent.clientX
      // Moving left increases width for a right-side sidebar
      const deltaX = startX - currentX
      const rawWidth = startWidth + deltaX

      if (rawWidth < 90) {
        currentWidth = 0
        if (!isCollapsed) handleClose()
        return
      }

      if (isCollapsed) {
        handleOpen()
      }

      const maxAllowed = Math.min(MAX_WIDTH, Math.floor(window.innerWidth * 0.48))
      const calculated = Math.max(MIN_WIDTH, Math.min(maxAllowed, rawWidth))
      currentWidth = calculated
      setWidth(calculated)
    }


    const onEnd = () => {
      setIsResizing(false)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
      try {
        if (currentWidth === 0) {
          localStorage.setItem('practiq_kb_collapsed', 'true')
        } else {
          localStorage.setItem('practiq_kb_collapsed', 'false')
          localStorage.setItem('practiq_kb_width', currentWidth.toString())
        }
      } catch {}
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onEnd)
      window.removeEventListener('touchmove', onMove)
      window.removeEventListener('touchend', onEnd)
    }

    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onEnd)
    window.addEventListener('touchmove', onMove, { passive: true })
    window.addEventListener('touchend', onEnd)
  }, [handleClose, handleOpen, isCollapsed])


  function handleMouseDown(e) {
    e.preventDefault()
    startResizing(e.clientX, width)
  }


  function handleTouchStart(e) {
    if (e.touches.length === 1) {
      startResizing(e.touches[0].clientX, width)
    }
  }


  function handleResetWidth() {
    setWidth(DEFAULT_WIDTH)
    try {
      localStorage.setItem('practiq_kb_width', DEFAULT_WIDTH.toString())
    } catch {}
  }


  function handleDragOver(e) {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
  }


  function handleDragLeave(e) {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
  }


  function handleDrop(e) {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
    const files = Array.from(e.dataTransfer?.files || [])
    if (files.length && onUploadFiles) {
      onUploadFiles(files)
    }
  }

  if (isCollapsed) {
    return (
      <div className="kb-collapsed-rail" aria-label="Knowledge Base (Collapsed)">
        <button
          type="button"
          className="kb-edge-toggle-btn is-collapsed"
          onClick={handleOpen}
          title="Open knowledge base"
          aria-label="Open knowledge base sidebar"
        >
          <svg
            width="11"
            height="11"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>
      </div>
    )
  }

  return (
    <aside
      className={`kb-sidebar-panel ${isResizing ? 'is-resizing' : ''} ${isDragOver ? 'is-dragging' : ''}`}
      style={{
        width: `${width}px`,
        flex: `0 0 ${width}px`,
      }}
      aria-label="Knowledge Base"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Left Divider Zone with Edge Toggle Button and Resizer */}
      <div
        className={`kb-divider-zone ${isNearDivider ? 'is-hovered' : ''}`}
        onMouseEnter={() => setIsNearDivider(true)}
        onMouseLeave={() => setIsNearDivider(false)}
      >
        <button
          type="button"
          className={`kb-edge-toggle-btn is-open ${isNearDivider ? 'is-visible' : ''}`}
          onClick={handleClose}
          title="Close knowledge base"
          aria-label="Close knowledge base sidebar"
        >
          <svg
            width="11"
            height="11"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>

        <div
          className={`kb-resizer-handle ${isResizing ? 'is-active' : ''}`}
          onMouseDown={handleMouseDown}
          onTouchStart={handleTouchStart}
          onDoubleClick={handleResetWidth}
          role="separator"
          aria-orientation="vertical"
          aria-valuenow={width}
          aria-valuemin={MIN_WIDTH}
          aria-valuemax={MAX_WIDTH}
          aria-label="Resize knowledge base"
          title="Drag to resize knowledge base · Double-click to reset"
        />
      </div>



      {/* Body: Document list or Empty state */}
      <div className="kb-body">
        {scopedNode && (
          <div className="kb-scoped-notice">
            <div className="kb-scoped-copy">
              <span className="kb-scoped-label">Active Scope</span>
              <strong className="kb-scoped-title" title={scopedNode.title}>
                {scopedNode.title}
              </strong>
            </div>
            {onClearScope && (
              <button
                type="button"
                className="kb-scoped-clear"
                onClick={onClearScope}
                title="Clear section scope"
                aria-label="Clear section scope"
              >
                ×
              </button>
            )}
          </div>
        )}

        {documents.length === 0 ? (
          <div className="kb-empty-notice">
            <span className="kb-empty-dash">—</span>
            <p>No documents added</p>
            <span>Upload PDFs to build your knowledge base</span>
            <div className="kb-empty-actions">
              <button
                type="button"
                className="kb-empty-upload-btn"
                onClick={onUploadClick}
                disabled={isUploading}
              >
                {isUploading ? 'Uploading...' : '+ Upload PDF'}
              </button>
            </div>
          </div>
        ) : (
          <div className="kb-documents-container">
            <div className="kb-documents-list" role="list">
              {documents.map((doc, index) => (
                <div
                  key={doc.documentId || doc.fileName || index}
                  className="kb-doc-card"
                  role="listitem"
                >
                  <div className="kb-doc-card-main">
                    <div className="kb-doc-icon-wrapper" aria-hidden="true">
                      <svg
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                        <line x1="16" y1="13" x2="8" y2="13" />
                        <line x1="16" y1="17" x2="8" y2="17" />
                        <line x1="10" y1="9" x2="8" y2="9" />
                      </svg>
                    </div>

                    <div className="kb-doc-info">
                      <div className="kb-doc-title-row">
                        <span className="kb-doc-title" title={doc.fileName || doc.title}>
                          {doc.title || doc.fileName}
                        </span>
                      </div>
                      <div className="kb-doc-meta">
                        <span>{doc.status === 'processing' ? 'Indexing…' : doc.status === 'failed' ? 'Upload failed' : `${doc.pages || 0} pages`}</span>
                        {doc.chunks ? (
                          <>
                            <span className="kb-doc-sep">·</span>
                            <span>{doc.chunks} chunks</span>
                          </>
                        ) : null}
                      </div>
                    </div>
                  </div>

                    <button
                      type="button"
                      className="kb-doc-remove-btn"
                      disabled={doc.status === 'processing'}
                      onClick={(e) => {
                        e.stopPropagation()
                        onRemovePdf?.(doc)
                      }}
                      title={`Remove ${doc.title || doc.fileName}`}
                      aria-label={`Remove ${doc.title || doc.fileName}`}
                    >
                      ×
                    </button>
                  </div>
                ))}
            </div>

            <button
              type="button"
              className="kb-add-more-btn"
              onClick={onUploadClick}
              disabled={isUploading}
            >
              <svg
                width="13"
                height="13"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
              <span>{isUploading ? 'Uploading...' : 'Add another PDF'}</span>
            </button>
          </div>
        )}
      </div>

      {/* Footer */}
      {documents.length > 0 && onClearAll && (
        <div className="kb-footer">
          <button
            type="button"
            className="kb-clear-all-btn"
            onClick={onClearAll}
            title="Clear all documents from knowledge base"
          >
            Clear Knowledge Base
          </button>
        </div>
      )}
    </aside>
  )
}
