import { useLayoutEffect, useSyncExternalStore } from 'react'
import { StreamingMessage } from './StreamingMessage'


export function StreamingReply({ store, components, onLayout, isStreaming = true }) {
  const { content, blocks, tail, status, sources, citations } = useSyncExternalStore(store.subscribe, store.getSnapshot)
  useLayoutEffect(() => { onLayout?.() }, [content, status, onLayout])
  return <>
    {isStreaming && status && !content && <p className="response-progress" role="status">{status}</p>}
    <StreamingMessage content={content} blocks={blocks} tail={tail} components={components}
      sources={sources} citations={citations} isStreaming={isStreaming} />
  </>
}
