export function observeChatScroll(element, state, onChange) {
  function pause() {
    state.paused = true
    onChange({ showLatest: true })
  }


  function wheel(event) {
    if (event.deltaY < 0) pause()
  }


  function touchStart(event) {
    state.touchY = event.touches[0]?.clientY ?? null
  }


  function touchMove(event) {
    const y = event.touches[0]?.clientY
    if (state.touchY !== null && y !== undefined && y > state.touchY + 8) pause()
  }


  function scroll() {
    const top = element.scrollTop
    const nearBottom = element.scrollHeight - element.clientHeight - top <= 40
    onChange({ fade: top > 8 })
    if (state.programmatic) {
      state.lastTop = top
      return
    }
    if (top < state.lastTop - 6 && !nearBottom) pause()
    state.lastTop = top
    if (nearBottom) {
      state.paused = false
      onChange({ showLatest: false })
    } else if (state.paused) {
      onChange({ showLatest: true })
    }
  }
  const listeners = { scroll, wheel, touchstart: touchStart, touchmove: touchMove }
  scroll()
  for (const [name, handler] of Object.entries(listeners)) {
    element.addEventListener(name, handler, { passive: true })
  }
  return () => {
    for (const [name, handler] of Object.entries(listeners)) {
      element.removeEventListener(name, handler)
    }
  }
}
