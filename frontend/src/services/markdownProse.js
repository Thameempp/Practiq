// Transform prose without changing fenced examples or inline code spans.
export function mapMarkdownProse(text, transform) {
  const inline = (value) => {
    let output = '', cursor = 0
    for (const match of value.matchAll(/(`+)(?!`)[\s\S]*?\1(?!`)/g)) {
      output += transform(value.slice(cursor, match.index)) + match[0]
      cursor = match.index + match[0].length
    }
    return output + transform(value.slice(cursor))
  }
  let fence = null, prose = '', output = ''
  for (const line of text.split(/(?<=\n)/)) {
    const marker = line.match(/^ {0,3}(`{3,}|~{3,})([^\n]*)/)
    if (fence) {
      output += line
      if (marker && marker[1][0] === fence[0] && marker[1].length >= fence.length && !marker[2].trim()) fence = null
    } else if (marker) {
      output += inline(prose) + line
      prose = ''; fence = marker[1]
    } else prose += line
  }
  return output + inline(prose)
}
