import { useEffect, useLayoutEffect, useRef } from 'react'


export function useComposerMotion(hasMessages) {
  const element = useRef(null)
  const previous = useRef(null)
  const animation = useRef(null)
  useLayoutEffect(() => {
    if (!element.current) return
    const rect = element.current.getBoundingClientRect()
    const last = previous.current
    if (last && last.hasMessages !== hasMessages && last.rect.top > 0 && rect.top > 0) {
      const delta = last.rect.top - rect.top
      if (Math.abs(delta) > 8 && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        animation.current?.cancel()
        animation.current = element.current.animate([
          { transform: `translateY(${delta}px)` },
          { transform: 'translateY(0)' },
        ], { duration: 480, easing: 'cubic-bezier(0.16, 1, 0.3, 1)' })
      }
    }
    previous.current = { rect, hasMessages }
  })
  useEffect(() => () => animation.current?.cancel(), [])
  return element
}
