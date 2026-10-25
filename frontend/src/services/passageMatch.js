// Keep a map to the actual PDF.js text characters; PyMuPDF offsets are not DOM offsets.
export function normalizedCharacters(parts, lineEnds = []) {
  let text = ''
  const positions = []
  const breaks = new Set(lineEnds)
  parts.forEach((part, index) => {
    let offset = 0
    for (const character of part) {
      const lineHyphen = /[-‐]/u.test(character) && breaks.has(index)
        && !part.slice(offset + character.length).trim() && /\p{L}$/u.test(part.slice(0, offset))
        && /^\p{L}/u.test((parts[index + 1] || '').trimStart())
      const normalized = lineHyphen ? '' : character.normalize('NFKC').toLowerCase()
        .replace(/[\s\u00ad]/gu, '').replace(/[‐‑]/gu, '-')
      for (const value of normalized) {
        text += value
        for (let unit = 0; unit < value.length; unit++) positions.push({ index, offset, end: offset + character.length })
      }
      offset += character.length
    }
  })
  return { text, positions }
}


export function matchPassage(parts, quote, lineEnds = []) {
  const needle = normalizedCharacters([quote]).text
  if (needle.length < 24) return null
  const variants = [normalizedCharacters(parts)]
  if (lineEnds.length) variants.push(normalizedCharacters(parts, lineEnds))
  const matches = new Map()
  for (const { text, positions } of variants) {
    const start = text.indexOf(needle)
    if (start < 0) continue
    if (text.indexOf(needle, start + 1) >= 0) return null
    const match = { start: positions[start], end: positions[start + needle.length - 1] }
    matches.set(JSON.stringify(match), match)
  }
  return matches.size === 1 ? [...matches.values()][0] : null
}
