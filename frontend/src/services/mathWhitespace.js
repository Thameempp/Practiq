// PDF/model output can contain Unicode spaces for which KaTeX has no metrics.
export function normalizeMathWhitespace() {
  function visit(node, insideMath) {
    const classes = node.properties?.className || []
    const math = insideMath || (node.type === 'element'
      && classes.some((name) => ['language-math', 'math-inline', 'math-display'].includes(name)))
    if (math && node.type === 'text') node.value = node.value.replace(/[\u00a0\u2007\u2009\u202f]/g, ' ')
    for (const child of node.children || []) visit(child, math)
  }
  return (tree) => visit(tree, false)
}
