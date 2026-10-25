import { matchPassage } from '../../services/passageMatch.js'


export function highlightPassage(layer, quote, surface, overlay) {
  const lineEnds = layer.textDivs.flatMap((div, index) => div.nextSibling?.nodeName === 'BR' ? [index] : [])
  const match = matchPassage(layer.textContentItemsStr, quote, lineEnds)
  if (!match) return false
  const start = layer.textDivs[match.start.index]?.firstChild
  const end = layer.textDivs[match.end.index]?.firstChild
  if (!start || !end) return false
  const range = document.createRange()
  range.setStart(start, match.start.offset)
  range.setEnd(end, match.end.end)
  const parent = surface.getBoundingClientRect()
  for (const rect of range.getClientRects()) {
    if (rect.width <= 0 || rect.height <= 0) continue
    const mark = document.createElement('span')
    mark.className = 'pdf-passage-mark'
    Object.assign(mark.style, { left: `${rect.left - parent.left}px`, top: `${rect.top - parent.top}px`,
      width: `${rect.width}px`, height: `${rect.height}px` })
    overlay.append(mark)
  }
  overlay.firstElementChild?.scrollIntoView({ block: 'center', inline: 'nearest' })
  return overlay.childElementCount > 0
}
