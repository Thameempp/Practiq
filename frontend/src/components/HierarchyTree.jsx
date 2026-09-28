import { useCallback, useEffect, useMemo, useState } from 'react'
import { DOCUMENT_HIERARCHY } from '../data/documentHierarchy'

const DEFAULT_WIDTH = 270
const MIN_WIDTH = 180
const MAX_WIDTH = 550

export function HierarchyTree({
  scopedNode,
  onSelectScope,
  onInspectNode,
  onActionPrompt,
  currentPdf,
}) {
  const [openMenuId, setOpenMenuId] = useState(null)
  const [width, setWidth] = useState(() => {
    try {
      const saved = localStorage.getItem('practiq_hierarchy_width')
      if (saved) {
        const parsed = parseInt(saved, 10)
        if (!isNaN(parsed) && parsed >= MIN_WIDTH && parsed <= MAX_WIDTH) {
          return parsed
        }
      }
    } catch {
      // ignore localStorage error
    }
    return DEFAULT_WIDTH
  })
  const [isCollapsed, setIsCollapsed] = useState(() => {
    try {
      return localStorage.getItem('practiq_hierarchy_collapsed') === 'true'
    } catch {
      return false
    }
  })
  const [isResizing, setIsResizing] = useState(false)
  const [isNearDivider, setIsNearDivider] = useState(false)

  useEffect(() => {
    return () => {
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
  }, [])

  function handleClose() {
    setIsCollapsed(true)
    try {
      localStorage.setItem('practiq_hierarchy_collapsed', 'true')
    } catch {
      // ignore
    }
  }

  function handleOpen() {
    setIsCollapsed(false)
    if (width < MIN_WIDTH) {
      setWidth(DEFAULT_WIDTH)
    }
    try {
      localStorage.setItem('practiq_hierarchy_collapsed', 'false')
    } catch {
      // ignore
    }
  }

  const startResizing = useCallback((startX, startWidth) => {
    setIsResizing(true)
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'

    let currentWidth = startWidth

    const onMove = (moveEvent) => {
      const currentX = moveEvent.touches ? moveEvent.touches[0].clientX : moveEvent.clientX
      const deltaX = currentX - startX
      const rawWidth = startWidth + deltaX
      if (rawWidth < 90) {
        currentWidth = 0
        setIsCollapsed(true)
        return
      }
      setIsCollapsed(false)
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
          localStorage.setItem('practiq_hierarchy_collapsed', 'true')
        } else {
          localStorage.setItem('practiq_hierarchy_collapsed', 'false')
          localStorage.setItem('practiq_hierarchy_width', currentWidth.toString())
        }
      } catch {
        // ignore
      }
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onEnd)
      window.removeEventListener('touchmove', onMove)
      window.removeEventListener('touchend', onEnd)
    }

    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onEnd)
    window.addEventListener('touchmove', onMove, { passive: true })
    window.addEventListener('touchend', onEnd)
  }, [])

  function handleMouseDown(e) {
    e.preventDefault()
    startResizing(e.clientX, width)
  }

  function handleTouchStart(e) {
    if (e.touches.length === 1) {
      startResizing(e.touches[0].clientX, width)
    }
  }

  function handleResetWidth(e) {
    e.stopPropagation()
    setWidth(DEFAULT_WIDTH)
    setIsCollapsed(false)
    try {
      localStorage.setItem('practiq_hierarchy_collapsed', 'false')
      localStorage.setItem('practiq_hierarchy_width', DEFAULT_WIDTH.toString())
    } catch {
      // ignore
    }
  }

  const scopedDescendantIds = useMemo(() => {
    if (!scopedNode) return new Set()
    const ids = new Set()
    function collect(node) {
      if (!node?.children) return
      for (const child of node.children) {
        ids.add(child.id)
        collect(child)
      }
    }
    collect(scopedNode)
    return ids
  }, [scopedNode])

  function handleNodeClick(node, e) {
    e.stopPropagation()
    if (scopedNode?.id === node.id) {
      onSelectScope(null)
    } else {
      onSelectScope(node)
    }
  }

  function handleMenuToggle(nodeId, e) {
    e.stopPropagation()
    setOpenMenuId((prev) => (prev === nodeId ? null : nodeId))
  }

  function handleAction(prompt, e) {
    e.stopPropagation()
    setOpenMenuId(null)
    onActionPrompt(prompt)
  }

  function getMenuActions(node, parent, level) {
    if (level === 1) {
      return [
        {
          label: '⚡ Summarize',
          prompt: `Summarize "${node.title}" in 3 concise bullet points.`,
        },
        {
          label: '💡 Explain',
          prompt: `Explain "${node.title}" in simple terms with an analogy.`,
        },
        {
          label: '📝 Quiz',
          prompt: `Generate 3 practice quiz questions based on "${node.title}".`,
        },
      ]
    }

    if (level === 2) {
      return [
        {
          label: '💡 Explain',
          prompt: `Explain "${node.title}" in detail with examples.`,
        },
      ]
    }

    return [
      {
        label: '💡 Explain',
        prompt: `Explain the concept of "${node.title}" from ${parent.title}.`,
      },
    ]
  }

  function renderTreeNode(node, level = 1, parent = null) {
    const isScoped = scopedNode?.id === node.id
    const isInScopedGroup = scopedDescendantIds.has(node.id)
    const children = node.children || []
    const hasChildren = children.length > 0
    const actions = getMenuActions(node, parent, level)

    return (
      <li
        className={`ascii-tree-item ${isScoped ? 'is-scoped-parent' : ''} ${isInScopedGroup ? 'is-in-scoped-group' : ''}`}
        key={node.id}
      >
        <div
          className={`ascii-row level-${level} ${isScoped ? 'is-scoped' : ''} ${isInScopedGroup ? 'is-scoped-group-item' : ''}`}
          onClick={(e) => handleNodeClick(node, e)}
        >
          <span className="ascii-node-dot" aria-hidden="true" />
          <span className="ascii-title" title={node.title}>{node.title}</span>

          <div className="ascii-row-tools" onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              className="ascii-more-btn"
              onClick={(e) => handleMenuToggle(node.id, e)}
              title="Actions"
            >
              ···
            </button>

            {openMenuId === node.id && (
              <div className="ascii-menu" onClick={(e) => e.stopPropagation()}>
                <button
                  type="button"
                  className="ascii-menu-item"
                  onClick={(e) => {
                    handleNodeClick(node, e)
                    setOpenMenuId(null)
                  }}
                >
                  {isScoped ? 'Clear Scope' : '🎯 Scope Retrieval'}
                </button>
                {actions.map((action) => (
                  <button
                    type="button"
                    className="ascii-menu-item"
                    key={action.label}
                    onClick={(e) => handleAction(action.prompt, e)}
                  >
                    {action.label}
                  </button>
                ))}
                <button
                  type="button"
                  className="ascii-menu-item"
                  onClick={() => {
                    setOpenMenuId(null)
                    onInspectNode(node)
                  }}
                >
                  📖 Read Text
                </button>
              </div>
            )}
          </div>
        </div>

        {hasChildren && (
          <ul className={`ascii-tree-list ${isScoped || isInScopedGroup ? 'is-scoped-group-list' : ''}`}>
            {children.map((child) => renderTreeNode(child, level + 1, node))}
          </ul>
        )}
      </li>
    )
  }

  if (isCollapsed) {
    return (
      <div className="hierarchy-collapsed-rail" aria-label="Document Tree (Collapsed)">
        <button
          type="button"
          className="hierarchy-edge-toggle-btn is-collapsed"
          onClick={handleOpen}
          title="Open hierarchy"
          aria-label="Open document hierarchy"
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
      </div>
    )
  }

  return (
    <aside
      className={`ascii-hierarchy-panel ${isResizing ? 'is-resizing' : ''}`}
      style={{
        width: `${width}px`,
        flex: `0 0 ${width}px`,
      }}
      aria-label="Document Tree"
      onClick={() => setOpenMenuId(null)}
    >
      <div className="ascii-tree-body">
        {!currentPdf ? (
          <div className="ascii-tree-empty-notice">
            <span className="tree-empty-dash">—</span>
            <p>No document loaded</p>
            <span>Upload a PDF to view document hierarchy</span>
          </div>
        ) : (
          <ul className="ascii-tree-list ascii-tree-root">
            {DOCUMENT_HIERARCHY.map((chapter) => renderTreeNode(chapter))}
          </ul>
        )}
      </div>

      {/* Floating Center-Aligned Divider Zone with Toggle Button and Resizer */}
      <div
        className={`hierarchy-divider-zone ${isNearDivider ? 'is-hovered' : ''}`}
        onMouseEnter={() => setIsNearDivider(true)}
        onMouseLeave={() => setIsNearDivider(false)}
      >
        <button
          type="button"
          className={`hierarchy-edge-toggle-btn is-open ${isNearDivider ? 'is-visible' : ''}`}
          onClick={handleClose}
          title="Close hierarchy"
          aria-label="Close document hierarchy"
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

        <div
          className={`ascii-resizer-handle ${isResizing ? 'is-active' : ''}`}
          onMouseDown={handleMouseDown}
          onTouchStart={handleTouchStart}
          onDoubleClick={handleResetWidth}
          role="separator"
          aria-orientation="vertical"
          aria-valuenow={width}
          aria-valuemin={MIN_WIDTH}
          aria-valuemax={MAX_WIDTH}
          aria-label="Resize document hierarchy"
          title="Drag to resize hierarchy · Double-click to reset"
        />
      </div>
    </aside>
  )
}
