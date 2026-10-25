import { useEffect, useMemo, useRef, useState } from 'react'
import { ChatMessage } from './components/ChatMessage'
import { HierarchyTree } from './components/HierarchyTree'
import { KnowledgeBaseSidebar } from './components/KnowledgeBaseSidebar'
import { PracticeArena } from './components/PracticeArena'
import { useKnowledgeBaseSync } from './hooks/useKnowledgeBaseSync'
import { useTextStream } from './hooks/useTextStream'
import { useConversation } from './hooks/useConversation'
import { usePdfUploads } from './hooks/usePdfUploads'
import { useBackendHealth } from './hooks/useBackendHealth'
import { useTheme } from './hooks/useTheme'
import { useStoredValue } from './hooks/useStoredValue'
import { useChatScroll } from './hooks/useChatScroll'
import { useComposerMotion } from './hooks/useComposerMotion'
import { ChatComposer } from './components/ChatComposer'
import { MarkdownTable } from './components/MarkdownTable'
import { outlineTitles, buildScopePayload } from './services/documentScope'
import { deletePdf, deletePdfs } from './services/documentsApi'
import { buildQuestionRequest } from './services/questionRequest'
import logoLight from './assets/logo-light.svg'
import logoDark from './assets/logo-dark.svg'
import './App.css'

import { API_URL } from './services/apiConfig'

const markdownComponents = { table: MarkdownTable }


function App() {
  const { conversationId, messages, setMessages, resetConversation } = useConversation()
  const [question, setQuestion] = useState('')
  const [scopedNode, setScopedNode] = useState(null)
  const [activeMode, setActiveMode] = useState('chat') // 'chat' | 'practice'
  const [currentPdf, setCurrentPdf] = useStoredValue('practiq_pdf', null)
  const [knowledgeBase, setKnowledgeBase] = useStoredValue('practiq_knowledge_base', [])
  const [documentHierarchy, setDocumentHierarchy] = useStoredValue('practiq_hierarchy', [])
  const [isKbCollapsed, setIsKbCollapsed] = useState(() => {
    try {
      return localStorage.getItem('practiq_kb_collapsed') === 'true'
    } catch {
      return false
    }
  })


  function toggleKb() {
    setIsKbCollapsed((prev) => {
      const next = !prev
      try {
        localStorage.setItem('practiq_kb_collapsed', String(next))
      } catch {}
      return next
    })
  }

  const effectiveKnowledgeBase = useMemo(() => {
    if (knowledgeBase && knowledgeBase.length > 0) return knowledgeBase
    if (currentPdf) return [currentPdf]
    return []
  }, [knowledgeBase, currentPdf])
  const fileInputRef = useRef(null)
  const composerContainerRef = useComposerMotion(messages.length > 0)

  const [isDraggingOver, setIsDraggingOver] = useState(false)
  const [uploadError, setUploadError] = useState('')

  const { isUploading, uploadFiles } = usePdfUploads(API_URL, (uploadedPdf) => {
    setCurrentPdf(uploadedPdf)
    setKnowledgeBase((current) => [
      ...current.filter((doc) => doc.documentId !== uploadedPdf.documentId),
      uploadedPdf,
    ])
    setDocumentHierarchy((current) => [
      ...current.filter((node) => node.documentId !== uploadedPdf.documentId),
      ...uploadedPdf.hierarchy,
    ])
    setIsKbCollapsed(false)
    try {
      localStorage.setItem('practiq_kb_collapsed', 'false')
    } catch {}
  }, setUploadError)

  useKnowledgeBaseSync(API_URL, effectiveKnowledgeBase, (documents) => {
    setKnowledgeBase(documents)
    setScopedNode((current) => (
      documents.some((doc) => doc.documentId === current?.documentId) ? current : null
    ))
    setCurrentPdf((current) => (
      documents.find((doc) => doc.documentId === current?.documentId) || documents[0] || null
    ))
    setDocumentHierarchy((current) => {
      const known = new Set(documents.map((doc) => doc.documentId))
      const server = documents.flatMap((doc) => doc.hierarchy || [])
      const serverIds = new Set(server.map((node) => node.documentId))
      return [
        ...server,
        ...current.filter((node) => known.has(node.documentId) && !serverIds.has(node.documentId)),
      ]
    })
  }, setUploadError, isUploading)


  function handleFileUpload(event) {
    const files = Array.from(event.target.files || [])
    if (!files.length) return

    uploadFiles(files)
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
    const files = Array.from(e.dataTransfer?.files || [])
    uploadFiles(files)
  }


  function handleSelectScope(node) {
    setScopedNode(node)
    if (!node) {
      setActiveMode('chat')
    }
  }


  function clearDocumentCache(documentId) {
    if (!documentId) return

    try {
      const cachePrefix = `practiq_mcq_${documentId}_`
      Object.keys(localStorage)
        .filter((key) => key.startsWith(cachePrefix))
        .forEach((key) => localStorage.removeItem(key))
    } catch {}
  }


  function forgetPdfs(removed) {
    const removedIds = new Set(removed.map((pdf) => pdf.documentId))
    const nextKb = effectiveKnowledgeBase.filter((pdf) => !removedIds.has(pdf.documentId))
    stopStream()
    removed.forEach((pdf) => clearDocumentCache(pdf.documentId))
    setKnowledgeBase((current) => (current.length ? current : effectiveKnowledgeBase)
      .filter((pdf) => !removedIds.has(pdf.documentId)))
    setScopedNode((current) => removedIds.has(current?.documentId) ? null : current)
    setDocumentHierarchy((current) => current.filter((node) => !removedIds.has(node.documentId)))
    setCurrentPdf((current) => removedIds.has(current?.documentId) ? nextKb[0] || null : current)
    if (!nextKb.length) resetConversation()
  }


  async function handleRemovePdf(pdfToRemove) {
    try {
      await deletePdf(API_URL, pdfToRemove)
      forgetPdfs([pdfToRemove])
      setUploadError('')
    } catch (removeError) {
      setUploadError(removeError.message || 'Could not remove the PDF.')
    }
  }


  async function handleClearAllKnowledgeBase() {
    const { removed, errors } = await deletePdfs(API_URL, effectiveKnowledgeBase)
    if (removed.length) forgetPdfs(removed)
    setUploadError(errors.length ? `${errors.length} PDF(s) could not be removed. ${errors[0].message}` : '')
  }
  const [theme, toggleTheme] = useTheme()
  const [isBackendOnline, setIsBackendOnline] = useBackendHealth(API_URL)

  const messagesEndRef = useRef(null)
  const completionSoundRef = useRef(null)
  const {
    store,
    isStreaming,
    error,
    startStream,
    stopStream,
  } = useTextStream()

  const { messagesRef, followStream, scrollToLatest, showConversationFade, showScrollToLatest } = useChatScroll(messages, isStreaming, activeMode)

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


  async function askQuestion(value = question, customScope = scopedNode, selectionId = null) {
    const trimmedQuestion = (typeof value === 'string' ? value : question).trim()

    if (!trimmedQuestion || isStreaming) return

    setQuestion('')

    scrollToLatest()

    const scopeForBackend = customScope ? buildScopePayload(customScope) : null

    const replyId = crypto.randomUUID()
    setMessages((current) => [
      ...current,
      {
        id: crypto.randomUUID(),
        role: 'user',
        content: trimmedQuestion,
        scope: customScope
          ? { title: customScope.title, pageLabel: customScope.pageLabel || `p. ${customScope.page}` }
          : null,
      },
      { id: replyId, role: 'assistant', content: '' },
    ])

    try {
      await startStream({
        url: `${API_URL}/ask`,
        body: buildQuestionRequest({
          question: trimmedQuestion,
          scope: scopeForBackend,
          conversationId: conversationId.current,
          documents: effectiveKnowledgeBase,
          selectionId,
          outline: outlineTitles(documentHierarchy, currentPdf?.documentId),
        }),
        onSettled: (content, metadata) => {
          setMessages((current) => current.map((message) => (
            message.id === replyId ? { ...message, content, ...metadata } : message
          )))
        },
        onRoute: (route) => {
          const choices = ['clarification_required', 'not_found'].includes(route.status) ? route.documents : []
          setMessages((current) => current.map((message) => message.id === replyId
            ? { ...message, documentChoices: choices } : message))
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
      console.error(requestError)
    }
  }


  function handleSubmit(event) {
    event.preventDefault()
    askQuestion()
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="topbar-left">
          {effectiveKnowledgeBase.length > 0 && (
            <>
              <img
                src={theme === 'dark' ? logoDark : logoLight}
                alt="Practiq logo"
                className="topbar-logo"
                width="20"
                height="20"
              />
              <p className="eyebrow">Practiq</p>
            </>
          )}
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
        {effectiveKnowledgeBase.length > 0 && (
          <HierarchyTree
            scopedNode={scopedNode}
            onSelectScope={handleSelectScope}
            currentPdf={currentPdf}
            hierarchy={documentHierarchy}
          />
        )}

        {/* Right / Center: Chat & Q&A Panel */}
        <div className="chat-panel">
          <input
            type="file"
            ref={fileInputRef}
            accept="application/pdf"
            multiple
            style={{ display: 'none' }}
            onChange={handleFileUpload}
          />

          {effectiveKnowledgeBase.length === 0 ? (
            <div
              className={`pdf-upload-center-view${isDraggingOver ? ' is-dragging' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className="upload-hero-brand">
                <img
                  src={theme === 'dark' ? logoDark : logoLight}
                  alt="Practiq logo"
                  className="upload-hero-logo"
                  width="64"
                  height="64"
                />
                <h1 className="upload-hero-title">Practiq</h1>
                <p className="upload-hero-description">
                  Explore concepts, find answers, and test your knowledge.
                </p>
              </div>

              <div className="upload-center-actions">
                <button
                  type="button"
                  className={`upload-center-plus-btn${isUploading ? ' is-loading' : ''}`}
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  aria-label={isUploading ? 'Uploading PDF...' : 'Upload PDF'}
                  title={isUploading ? 'Uploading PDF...' : 'Upload PDF'}
                >
                  {isUploading ? (
                    <svg
                      className="upload-spinner"
                      width="22"
                      height="22"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      aria-hidden="true"
                    >
                      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeOpacity="0.25" />
                      <path d="M12 3a9 9 0 0 1 9 9" stroke="currentColor" />
                    </svg>
                  ) : (
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
                  )}
                </button>
                <div className="upload-center-meta">
                  <span className="upload-center-title">
                    {isUploading ? 'Uploading PDF...' : isDraggingOver ? 'Drop PDF here' : 'Upload PDF'}
                  </span>
                  <span className="upload-center-subtitle">
                    or drag and drop here
                  </span>
                </div>
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
                        <img
                          src={theme === 'dark' ? logoDark : logoLight}
                          alt="Practiq logo"
                          className="empty-logo"
                          width="44"
                          height="44"
                        />
                        <span className="empty-label">READY</span>
                        <p>Ask a question about the document.</p>
                        <span className="empty-hint">
                          Select any section in the left tree to scope answers or run 1-click AI actions.
                        </span>
                      </div>
                    )}

                    {messages.map((message, index) => (
                      <ChatMessage key={message.id} message={message}
                        generating={message.role === 'assistant' && isStreaming && index === messages.length - 1}
                        choicesDisabled={isStreaming || index !== messages.length - 1}
                        store={store} components={markdownComponents} onLayout={followStream}
                        onSelectDocument={(id, filename) => askQuestion(filename, null, id)} />
                    ))}

                    <div ref={messagesEndRef} aria-hidden="true" />
                  </div>
                </div>

                {(error || uploadError) && (
                  <p className="error-message" role="alert">{error || uploadError}</p>
                )}

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

                  {scopedNode && (
                    <div className="composer-scope-pill">
                      <span className="scope-pill-dot" aria-hidden="true" />
                      <span className="scope-pill-text">
                        Focused on <strong>{scopedNode.title}</strong>
                      </span>
                      {scopedNode.page > 0 && (
                        <span className="scope-pill-page" title={`Topic starts on PDF page ${scopedNode.page}`}>
                          {scopedNode.page}
                        </span>
                      )}
                      <button
                        type="button"
                        className="scope-pill-clear"
                        onClick={() => handleSelectScope(null)}
                        title="Clear section focus"
                        aria-label="Clear section focus"
                      >
                        ×
                      </button>
                    </div>
                  )}

                  <ChatComposer question={question} setQuestion={setQuestion} messages={messages}
                    conversationId={conversationId.current} scope={scopedNode} isStreaming={isStreaming}
                    onSubmit={handleSubmit} onStop={stopStream} onNewChat={() => {
                      stopStream()
                      resetConversation()
                      setQuestion('')
                      setScopedNode(null)
                      setActiveMode('chat')
                    }} />
                </div>
              </div>

              {scopedNode && activeMode === 'practice' && (
                <PracticeArena
                  key={scopedNode.id}
                  node={scopedNode}
                  documentId={scopedNode.documentId || currentPdf?.documentId}
                  scope={buildScopePayload(scopedNode)}
                  onAskQuestion={(prompt) => {
                    setActiveMode('chat')
                    askQuestion(prompt, scopedNode)
                  }}
                />
              )}
            </>
          )}
        </div>
        {/* Right End: Knowledge Base Sidebar */}
        {effectiveKnowledgeBase.length > 0 && (
          <KnowledgeBaseSidebar
            documents={effectiveKnowledgeBase}
            onRemovePdf={handleRemovePdf}
            onClearAll={handleClearAllKnowledgeBase}
            onUploadClick={() => fileInputRef.current?.click()}
            onUploadFiles={(files) => uploadFiles(files)}
            isUploading={isUploading}
            scopedNode={scopedNode}
            onClearScope={() => handleSelectScope(null)}
            isCollapsed={isKbCollapsed}
            onToggleCollapse={toggleKb}
          />
        )}
      </section>

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
