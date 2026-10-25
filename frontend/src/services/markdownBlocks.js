// Scan only new lines. Hold lists, fences and display math until a safe boundary.
export function createMarkdownBlocks() {
  let previous = '', pending = '', cursor = 0, boundary = 0, fence = null, math = false
  let blocks = []
  return {
    update(content) {
      if (!content.startsWith(previous)) {
        previous = ''; pending = ''; cursor = 0; boundary = 0; fence = null; math = false; blocks = []
      }
      pending += content.slice(previous.length)
      previous = content
      let newline
      while ((newline = pending.indexOf('\n', cursor)) !== -1) {
        const line = pending.slice(cursor, newline)
        if (boundary && line.trim()) {
          const list = /^ {0,3}(?:[-+*]|\d+[.)])\s/.test(pending)
          const continuation = /^(?:\s+| {0,3}(?:[-+*]|\d+[.)])\s)/.test(line)
          if (!(list && continuation)) {
            blocks = [...blocks, { id: blocks.length, text: pending.slice(0, boundary) }]
            pending = pending.slice(boundary)
            cursor -= boundary
            newline -= boundary
          }
          boundary = 0
        }
        const marker = line.match(/^ {0,3}(`{3,}|~{3,})(.*)$/)
        if (marker && !math) {
          if (!fence) fence = marker[1]
          else if (marker[1][0] === fence[0] && marker[1].length >= fence.length && !marker[2].trim()) fence = null
        }
        if (!fence && (line.trim() === '$$' || line.trim() === '\\[' || line.trim() === '\\]')) {
          math = !math
        }
        cursor = newline + 1
        if (!fence && !math && !line.trim()) boundary = cursor
      }
      return { blocks, tail: pending }
    },
  }
}
