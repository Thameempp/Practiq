import { useCallback, useEffect, useRef, useState } from 'react'
import { readChatSession, saveChatSession } from '../services/chatSession.js'


export function useConversation() {
  const [initial] = useState(readChatSession)
  const conversationId = useRef(initial.id)
  const [messages, setMessages] = useState(initial.messages)


  const resetConversation = useCallback(() => {
    conversationId.current = crypto.randomUUID()
    setMessages([])
  }, [])
  useEffect(() => {
    saveChatSession(conversationId.current, messages)
  }, [messages])
  return { conversationId, messages, setMessages, resetConversation }
}
