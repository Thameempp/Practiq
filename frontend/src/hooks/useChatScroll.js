import { useCallback, useEffect, useRef, useState } from 'react'
import { observeChatScroll } from '../services/chatScroll.js'


export function useChatScroll(messages, isStreaming, mode) {
  const messagesRef = useRef(null)
  const state = useRef({ paused: false, programmatic: false, lastTop: 0, touchY: null })
  const frame = useRef(null)
  const timer = useRef(null)
  const [showConversationFade, setFade] = useState(false)
  const [showScrollToLatest, setShowLatest] = useState(false)


  const followStream = useCallback(() => {
    const element = messagesRef.current
    if (element && !state.current.paused) {
      element.scrollTop = element.scrollHeight
    }
  }, [])
  useEffect(() => {
    if (!messages.length || state.current.paused) return
    const id = requestAnimationFrame(followStream)
    return () => cancelAnimationFrame(id)
  }, [messages, isStreaming, followStream])
  useEffect(() => {
    if (!messagesRef.current) return
    return observeChatScroll(messagesRef.current, state.current, ({ fade, showLatest }) => {
      if (fade !== undefined) setFade(fade)
      if (showLatest !== undefined) setShowLatest(showLatest)
    })
  }, [messages.length, mode])
  useEffect(() => () => {
    cancelAnimationFrame(frame.current)
    clearTimeout(timer.current)
  }, [])


  const scrollToLatest = useCallback(() => {
    state.current.paused = false
    state.current.programmatic = true
    setShowLatest(false)
    cancelAnimationFrame(frame.current)
    clearTimeout(timer.current)
    frame.current = requestAnimationFrame(() => {
      const element = messagesRef.current
      if (!element) {
        state.current.programmatic = false
        return
      }
      element.scrollTo({ top: element.scrollHeight, behavior: 'smooth' })
      timer.current = setTimeout(() => {
        state.current.programmatic = false
        state.current.lastTop = messagesRef.current?.scrollTop || 0
      }, 450)
    })
  }, [])

  return { messagesRef, followStream, scrollToLatest, showConversationFade, showScrollToLatest }
}
