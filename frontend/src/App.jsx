import { Children, useEffect, useLayoutEffect, useRef, useState } from 'react'
import Lenis from 'lenis'
import { StreamingMessage } from './components/StreamingMessage'
import { HierarchyTree } from './components/HierarchyTree'
import { SectionInspector } from './components/SectionInspector'
import { PracticeArena } from './components/PracticeArena'
import { useTextStream } from './hooks/useTextStream'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const SAMPLE_PDF = {
  title: 'Computer Science: An Introduction',
  fileName: 'computer_science_sample.pdf',
  pages: 5,
}

function MarkdownTable({ children }) {
  const sections = Children.toArray(children)
  const body = sections.find((section) => section.type === 'tbody')
  const rows = body ? Children.toArray(body.props.children) : []

  return (
    <div className="markdown-table-list">
      {rows.map((row, rowIndex) => {
        const cells = Children.toArray(row.props.children)

        return (
          <section className="markdown-table-item" key={rowIndex}>
            {cells.map((cell, cellIndex) => (
              <div className="markdown-table-field" key={cellIndex}>
                <div>{cell.props.children}</div>
              </div>
            ))}
          </section>
        )
      })}
    </div>
  )
}

const markdownComponents = { table: MarkdownTable }

function App() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [scopedNode, setScopedNode] = useState(null)
  const [activeMode, setActiveMode] = useState('chat') // 'chat' | 'practice'
  const [inspectedNode, setInspectedNode] = useState(null)
  const [currentPdf, setCurrentPdf] = useState(() => {
    try {
      const saved = localStorage.getItem('practiq_pdf')
      if (saved) return JSON.parse(saved)
    } catch {}
    return null
  })
  const fileInputRef = useRef(null)
  const composerContainerRef = useRef(null)
  const lastComposerRectRef = useRef(null)
  const prevHadMessagesRef = useRef(messages.length > 0)

  // Smooth FLIP transition when composer moves between center and bottom
  useLayoutEffect(() => {
    const el = composerContainerRef.current
    if (!el) return

    const currentRect = el.getBoundingClientRect()
    const hadMessages = prevHadMessagesRef.current
    const hasMessages = messages.length > 0
    prevHadMessagesRef.current = hasMessages

    if (
      lastComposerRectRef.current &&
      lastComposerRectRef.current.top > 0 &&
      currentRect.top > 0 &&
      hadMessages !== hasMessages
    ) {
      const deltaY = lastComposerRectRef.current.top - currentRect.top

      if (Math.abs(deltaY) > 8) {
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

        if (!prefersReducedMotion) {
          el.style.transform = `translateY(${deltaY}px)`
          el.style.transition = 'none'

          // Force reflow to commit initial inverted position
          void el.offsetHeight

          requestAnimationFrame(() => {
            el.style.transition = 'transform 0.48s cubic-bezier(0.16, 1, 0.3, 1)'
            el.style.transform = 'translateY(0)'

            const onTransitionEnd = (e) => {
              if (e.target === el && e.propertyName === 'transform') {
                el.style.transition = ''
                el.style.transform = ''
                el.removeEventListener('transitionend', onTransitionEnd)
              }
            }
            el.addEventListener('transitionend', onTransitionEnd)
          })
        }
      }
    }

    lastComposerRectRef.current = currentRect
  })

  useEffect(() => {
    try {
      if (currentPdf) {
        localStorage.setItem('practiq_pdf', JSON.stringify(currentPdf))
      } else {
        localStorage.removeItem('practiq_pdf')
      }
    } catch {}
  }, [currentPdf])

  const [isDraggingOver, setIsDraggingOver] = useState(false)

  function handleFileUpload(event) {
    const file = event.target.files?.[0]
    if (!file) return

    setCurrentPdf({
      title: file.name.replace(/\.[^/.]+$/, ''),
      fileName: file.name,
      pages: Math.max(1, Math.round(file.size / 65000)) || 1,
    })
    setShowDocumentDetail(true)
    setError('')
    event.target.value = ''
  }

  function handleDragOver(e) {
    e.preventDefault()
    e.stopPropagation()
    setIsDraggingOver(true)
  }

  function handleDragLeave(e) {
    e.preventDefault()
    e.stopPropagation()
    setIsDraggingOver(false)
  }

  function handleDrop(e) {
    e.preventDefault()
    e.stopPropagation()
    setIsDraggingOver(false)
    const file = e.dataTransfer?.files?.[0]
    if (!file) return
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a valid PDF file.')
      return
    }
    setCurrentPdf({
      title: file.name.replace(/\.[^/.]+$/, ''),
      fileName: file.name,
      pages: Math.max(1, Math.round(file.size / 65000)) || 1,
    })
    setShowDocumentDetail(true)
    setError('')
  }

  function handleSelectScope(node) {
    setScopedNode(node)
    if (node) {
      setShowDocumentDetail(true)
    } else {
      setActiveMode('chat')
    }
  }
  const [showDocumentDetail, setShowDocumentDetail] = useState(true)
  const [theme, setTheme] = useState(() => {
    try {
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme === 'dark' || savedTheme === 'light') {
        return savedTheme
      }
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    } catch {
      return 'light'
    }
  })

  useEffect(() => {
    try {
      document.documentElement.setAttribute('data-theme', theme)
      document.documentElement.style.colorScheme = theme
      localStorage.setItem('theme', theme)
    } catch (e) {
      console.error(e)
    }
  }, [theme])

  function toggleTheme() {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))
  }

  const [isBackendOnline, setIsBackendOnline] = useState(true)

  useEffect(() => {
    let isMounted = true

    async function checkBackendHealth() {
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 2500)
        const response = await fetch(`${API_URL}/health`, {
          signal: controller.signal,
          cache: 'no-store',
        })
        clearTimeout(timeoutId)
        if (isMounted) {
          setIsBackendOnline(response.ok)
        }
      } catch {
        if (isMounted) {
          setIsBackendOnline(false)
        }
      }
    }

    checkBackendHealth()
    const intervalId = setInterval(checkBackendHealth, 4000)

    return () => {
      isMounted = false
      clearInterval(intervalId)
    }
  }, [])

  const messagesEndRef = useRef(null)
  const messagesRef = useRef(null)
  const lenisRef = useRef(null)
  const completionSoundRef = useRef(null)
  const shouldAutoScrollRef = useRef(true)
  const userPausedAutoScrollRef = useRef(false)
  const isProgrammaticScrollRef = useRef(false)
  const autoScrollRafRef = useRef(null)
  const touchStartYRef = useRef(null)
  const [showConversationFade, setShowConversationFade] = useState(false)
  const [showScrollToLatest, setShowScrollToLatest] = useState(false)

  const {
    isStreaming,
    error,
    startStream,
    stopStream,
  } = useTextStream()

  useEffect(() => {
    const completionSound = new Audio('/sounds/llm-complete.mp3')
    completionSound.preload = 'auto'
    completionSound.volume = 0.25
    completionSoundRef.current = completionSound

    return () => {
      completionSound.pause()
      completionSoundRef.current = null
    }
  }, [])

  // Initialize Lenis smooth scroll on the active messages container
  useEffect(() => {
    const messagesElement = messagesRef.current
    if (!messagesElement || !currentPdf) return undefined

    const contentElement = messagesElement.querySelector('.messages-content')
    if (!contentElement) return undefined

    const lenis = new Lenis({
      wrapper: messagesElement,
      content: contentElement,
      autoRaf: true,
      duration: 0.5,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
    })
    lenisRef.current = lenis

    function handleResize() {
      lenis.resize()
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      lenis.destroy()
      lenisRef.current = null
    }
  }, [currentPdf])

  // Smooth continuous auto-scroll during streaming
  useEffect(() => {
    if (!shouldAutoScrollRef.current || isProgrammaticScrollRef.current || !messages.length) {
      return undefined
    }

    if (autoScrollRafRef.current) {
      window.cancelAnimationFrame(autoScrollRafRef.current)
    }

    autoScrollRafRef.current = window.requestAnimationFrame(() => {
      const lenis = lenisRef.current
      const messagesElement = messagesRef.current
      const target = messagesEndRef.current
      if (!messagesElement || !target) return

      if (lenis) {
        lenis.resize()
        lenis.scrollTo(target, {
          duration: 0.28,
          easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
          force: true,
        })
      } else {
        target.scrollIntoView({ behavior: 'smooth' })
      }
    })

    return () => {
      if (autoScrollRafRef.current) {
        window.cancelAnimationFrame(autoScrollRafRef.current)
      }
    }
  }, [messages, isStreaming])

  // Scroll event listeners & detect user scroll-up during streaming
  useEffect(() => {
    const messagesElement = messagesRef.current
    if (!messagesElement || !currentPdf) return undefined

    function pauseAutoScroll() {
      userPausedAutoScrollRef.current = true
      shouldAutoScrollRef.current = false
      isProgrammaticScrollRef.current = false

      if (autoScrollRafRef.current) {
        window.cancelAnimationFrame(autoScrollRafRef.current)
      }

      if (lenisRef.current) {
        lenisRef.current.stop()
        lenisRef.current.start()
      }

      setShowScrollToLatest((prev) => (!prev ? true : prev))
    }

    function handleWheel(event) {
      if (event.deltaY < 0) {
        // User scrolled UP -> immediately pause auto-scroll and show button
        pauseAutoScroll()
      }
    }

    function handleTouchStart(event) {
      touchStartYRef.current = event.touches[0]?.clientY ?? null
    }

    function handleTouchMove(event) {
      const touchStartY = touchStartYRef.current
      const currentY = event.touches[0]?.clientY

      // Pulling down finger = scrolling UP
      if (touchStartY !== null && currentY !== undefined && currentY > touchStartY + 8) {
        pauseAutoScroll()
      }
    }

    function updateConversationFade() {
      const lenis = lenisRef.current
      const el = messagesRef.current
      if (!el) return

      const scrollTop = lenis ? lenis.scroll : el.scrollTop
      const scrollLimit = lenis ? lenis.limit : el.scrollHeight - el.clientHeight
      const distanceToBottom = scrollLimit - scrollTop
      const isNearBottom = distanceToBottom < 48

      setShowConversationFade((prev) => {
        const next = scrollTop > 4
        return prev !== next ? next : prev
      })

      // Skip updating auto-scroll state during programmatic smooth scroll
      if (isProgrammaticScrollRef.current) return

      if (isNearBottom) {
        userPausedAutoScrollRef.current = false
        shouldAutoScrollRef.current = true
        setShowScrollToLatest((prev) => (prev ? false : prev))
      } else if (userPausedAutoScrollRef.current) {
        shouldAutoScrollRef.current = false
        setShowScrollToLatest((prev) => (!prev ? true : prev))
      }
    }

    updateConversationFade()
    messagesElement.addEventListener('scroll', updateConversationFade, { passive: true })
    messagesElement.addEventListener('wheel', handleWheel, { passive: true })
    messagesElement.addEventListener('touchstart', handleTouchStart, { passive: true })
    messagesElement.addEventListener('touchmove', handleTouchMove, { passive: true })
    lenisRef.current?.on('scroll', updateConversationFade)

    return () => {
      messagesElement.removeEventListener('scroll', updateConversationFade)
      messagesElement.removeEventListener('wheel', handleWheel)
      messagesElement.removeEventListener('touchstart', handleTouchStart)
      messagesElement.removeEventListener('touchmove', handleTouchMove)
      lenisRef.current?.off('scroll', updateConversationFade)
    }
  }, [currentPdf, isStreaming, activeMode])

  async function askQuestion(value = question, customScope = scopedNode) {
    const trimmedQuestion = (typeof value === 'string' ? value : question).trim()

    if (!trimmedQuestion || isStreaming || !currentPdf) return

    setQuestion('')

    userPausedAutoScrollRef.current = false
    shouldAutoScrollRef.current = true
    isProgrammaticScrollRef.current = true
    setShowScrollToLatest(false)

    // Prepend scope context if active so RAG retrieval specifically focuses on the section
    const promptForBackend = customScope
      ? `[Scope: ${customScope.title} (${customScope.pageLabel || `p. ${customScope.page}`})] ${trimmedQuestion}`
      : trimmedQuestion

    setMessages((current) => [
      ...current,
      {
        role: 'user',
        content: trimmedQuestion,
        scope: customScope
          ? { title: customScope.title, pageLabel: customScope.pageLabel || `p. ${customScope.page}` }
          : null,
      },
      { role: 'assistant', content: '' },
    ])

    setTimeout(() => {
      isProgrammaticScrollRef.current = false
    }, 450)

    try {
      await startStream({
        url: `${API_URL}/ask`,
        body: { question: promptForBackend },
        onText: (content) => {
          setIsBackendOnline(true)
          setMessages((current) => current.map((message, index) => (
            index === current.length - 1
              ? { ...message, content }
              : message
          )))
        },
        onComplete: () => {
          setIsBackendOnline(true)
          const completionSound = completionSoundRef.current

          if (!completionSound) return

          completionSound.currentTime = 0
          completionSound.play().catch(() => {})
        },
      })
    } catch (requestError) {
      setIsBackendOnline(false)
      console.error(requestError)
    }
  }

  function handleSubmit(event) {
    event.preventDefault()
    askQuestion()
  }

  function scrollToLatest() {
    userPausedAutoScrollRef.current = false
    shouldAutoScrollRef.current = true
    isProgrammaticScrollRef.current = true
    setShowScrollToLatest(false)

    const lenis = lenisRef.current
    const target = messagesEndRef.current

    if (lenis && target) {
      lenis.resize()
      lenis.scrollTo(target, {
        duration: 0.48,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        force: true,
        onComplete: () => {
          isProgrammaticScrollRef.current = false
          shouldAutoScrollRef.current = true
          userPausedAutoScrollRef.current = false
        },
      })
    } else if (target) {
      target.scrollIntoView({ behavior: 'smooth' })
      setTimeout(() => {
        isProgrammaticScrollRef.current = false
        shouldAutoScrollRef.current = true
        userPausedAutoScrollRef.current = false
      }, 500)
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="topbar-left">
          <p className="eyebrow">Practiq</p>
        </div>

        <div className="topbar-right">
          <button
            type="button"
            className="theme-toggle-btn"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            <span className="theme-toggle-icon" aria-hidden="true">
              {theme === 'dark' ? (
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="5" />
                  <line x1="12" y1="1" x2="12" y2="3" />
                  <line x1="12" y1="21" x2="12" y2="23" />
                  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                  <line x1="1" y1="12" x2="3" y2="12" />
                  <line x1="21" y1="12" x2="23" y2="12" />
                  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                </svg>
              ) : (
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                </svg>
              )}
            </span>
          </button>
        </div>
      </header>

      <section className="workspace" aria-label="PDF research workspace">
        {/* Left End: Hierarchy Feature */}
        <HierarchyTree
          scopedNode={scopedNode}
          onSelectScope={handleSelectScope}
          onInspectNode={setInspectedNode}
          onActionPrompt={(prompt) => {
            setActiveMode('chat')
            askQuestion(prompt, scopedNode)
          }}
          currentPdf={currentPdf}
        />

        {/* Right / Center: Chat & Q&A Panel */}
        <div className="chat-panel">
          <input
            type="file"
            ref={fileInputRef}
            accept="application/pdf"
            style={{ display: 'none' }}
            onChange={handleFileUpload}
          />

          {!currentPdf ? (
            <div
              className={`pdf-upload-center-view${isDraggingOver ? ' is-dragging' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <button
                type="button"
                className="upload-center-plus-btn"
                onClick={() => fileInputRef.current?.click()}
                aria-label="Upload PDF"
                title="Upload PDF"
              >
                <svg
                  width="22"
                  height="22"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
              </button>
              <div className="upload-center-meta">
                <span className="upload-center-title">Upload PDF</span>
                <button
                  type="button"
                  className="upload-center-sample-btn"
                  onClick={() => {
                    setCurrentPdf(SAMPLE_PDF)
                    setShowDocumentDetail(true)
                  }}
                  title="Load sample Computer Science PDF"
                >
                  or try with sample PDF
                </button>
              </div>
            </div>
          ) : (
            <>
              {scopedNode && (
                <div className="chat-panel-top-switcher">
                  <div className="topic-mode-switcher" role="tablist" aria-label="Topic mode">
                    <div
                      className={`mode-slider-pill ${activeMode === 'practice' ? 'is-practice' : 'is-chat'}`}
                      aria-hidden="true"
                    />
                    <button
                      type="button"
                      role="tab"
                      id="tab-chat"
                      aria-selected={activeMode === 'chat'}
                      aria-controls="panel-chat-view"
                      className={`mode-tab-btn ${activeMode === 'chat' ? 'is-active' : ''}`}
                      onClick={() => setActiveMode('chat')}
                    >
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                      </svg>
                      <span>Chat</span>
                    </button>
                    <button
                      type="button"
                      role="tab"
                      id="tab-practice"
                      aria-selected={activeMode === 'practice'}
                      aria-controls="panel-practice-view"
                      className={`mode-tab-btn ${activeMode === 'practice' ? 'is-active' : ''}`}
                      onClick={() => setActiveMode('practice')}
                    >
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10" />
                        <circle cx="12" cy="12" r="6" />
                        <circle cx="12" cy="12" r="2" />
                      </svg>
                      <span>Practice</span>
                    </button>
                  </div>
                </div>
              )}

              <div
                className={`chat-conversation-area${!messages.length ? ' chat-not-started' : ''}`}
                style={{ display: scopedNode && activeMode === 'practice' ? 'none' : 'flex' }}
              >
                <div
                  className={`messages${showConversationFade ? ' has-scroll-fade' : ''}${isStreaming ? ' is-streaming' : ''}`}
                  ref={messagesRef}
                  aria-live="polite"
                >
                  <div className="messages-content">
                    {!messages.length && (
                      <div className="empty-state">
                        <div className="empty-line" />
                        <span className="empty-label">READY</span>
                        <p>Ask a question about the document.</p>
                        <span className="empty-hint">
                          Select any section in the left tree to scope answers or run 1-click AI actions.
                        </span>
                      </div>
                    )}

                    {messages.map((message, index) => (
                      <article className={`message ${message.role}`} key={`${message.role}-${index}`}>
                        <span className="message-role">{message.role === 'user' ? 'YOU' : 'PDF'}</span>
                        {message.role === 'assistant' ? (
                          <div className="markdown-content">
                            <StreamingMessage
                              content={message.content}
                              components={markdownComponents}
                            />
                          </div>
                        ) : (
                          <div className="user-message-container">
                            {message.scope && (
                              <div className="user-message-scope-tag">
                                <span>🎯 Scope: {message.scope.title} ({message.scope.pageLabel})</span>
                              </div>
                            )}
                            <p>{message.content}</p>
                          </div>
                        )}
                      </article>
                    ))}

                    <div ref={messagesEndRef} aria-hidden="true" />
                  </div>
                </div>

                {error && <p className="error-message" role="alert">{error}</p>}

                <div className="composer-container" ref={composerContainerRef}>
                  {messages.length > 0 && (
                    <button
                      className={`scroll-latest ${showScrollToLatest ? 'is-visible' : ''}`}
                      type="button"
                      onClick={scrollToLatest}
                      aria-label="Scroll to latest response"
                      title="Scroll to latest response"
                    >
                      <svg
                        width="13"
                        height="13"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        aria-hidden="true"
                      >
                        <polyline points="6 9 12 15 18 9" />
                      </svg>
                    </button>
                  )}

                  {showDocumentDetail && currentPdf && (
                    <div className="document-detail-banner" title={currentPdf.fileName}>
                      <div className="document-detail-left">
                        <span className="document-detail-dot" aria-hidden="true" />
                        <div className="document-detail-copy">
                          <strong>{currentPdf.title}</strong>
                          <span className="document-detail-pages">{currentPdf.pages} pages</span>
                          {scopedNode && (
                            <>
                              <span className="document-detail-sep">·</span>
                              <span className="document-detail-scope" title={`Focused on ${scopedNode.title}`}>
                                Focused on {scopedNode.title}
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                      <div className="document-detail-actions">
                        {isStreaming ? (
                          <div className="loading-row"><span /><span /><span /> Reading PDF</div>
                        ) : (
                          <span className="document-detail-type">PDF</span>
                        )}
                        <button
                          type="button"
                          className="document-detail-remove"
                          onClick={() => {
                            setCurrentPdf(null)
                            setScopedNode(null)
                            setMessages([])
                          }}
                          aria-label="Remove PDF"
                          title="Remove PDF"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                  )}

                  <form className="composer" onSubmit={handleSubmit}>
                    <button
                      type="button"
                      className="composer-add-pdf"
                      aria-label="Upload or replace PDF"
                      title="Upload or replace PDF"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      +
                    </button>
                    <textarea
                      value={question}
                      onChange={(event) => setQuestion(event.target.value)}
                      onKeyDown={(event) => {
                        if (event.key === 'Enter' && !event.shiftKey) {
                          event.preventDefault()
                          handleSubmit(event)
                        }
                      }}
                      placeholder={
                        scopedNode
                          ? `Ask specifically about ${scopedNode.title}...`
                          : 'Ask anything in the PDF...'
                      }
                      aria-label="Question"
                      rows="1"
                    />
                    {question.trim() && (
                      <button className="send-button" type="submit" disabled={isStreaming}>
                        Ask <span aria-hidden="true">↗</span>
                      </button>
                    )}
                    {isStreaming && (
                      <button className="stop-button" type="button" onClick={stopStream}>
                        Stop
                      </button>
                    )}
                  </form>
                  <p className="composer-note">Enter to ask · Shift + Enter for a new line</p>
                </div>
              </div>

              {scopedNode && activeMode === 'practice' && (
                <PracticeArena
                  key={scopedNode.id}
                  node={scopedNode}
                  onAskQuestion={(prompt) => {
                    setActiveMode('chat')
                    askQuestion(prompt, scopedNode)
                  }}
                />
              )}
            </>
          )}
        </div>
      </section>

      {/* Section Inspector Modal */}
      {inspectedNode && (
        <SectionInspector
          node={inspectedNode}
          onClose={() => setInspectedNode(null)}
          onScopeToggle={(node) => {
            if (scopedNode?.id === node.id) {
              handleSelectScope(null)
            } else {
              handleSelectScope(node)
            }
          }}
          isScoped={scopedNode?.id === inspectedNode.id}
          onActionPrompt={(prompt) => {
            setInspectedNode(null)
            askQuestion(prompt, inspectedNode)
          }}
        />
      )}

      {/* Bottom-right single backend status dot */}
      <div
        className="backend-status-indicator"
        title={
          isBackendOnline
            ? 'Backend connected (FastAPI on port 8000)'
            : 'Backend offline (server not running on port 8000)'
        }
        aria-label={isBackendOnline ? 'Backend connected' : 'Backend offline'}
      >
        <span
          className={`status-dot ${isBackendOnline ? 'is-online' : 'is-offline'}`}
          aria-hidden="true"
        />
      </div>
    </main>
  )
}

export default App
