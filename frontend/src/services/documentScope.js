const MAX_OUTLINE_TITLES = 60
const MIN_TOP_LEVEL_TITLES = 15


function collectTitles(nodes, depth, maxDepth, titles) {
  for (const node of nodes) {
    titles.push(node.title)
    if (depth < maxDepth) collectTitles(node.children || [], depth + 1, maxDepth, titles)
  }
}


// Chapter titles of one document; sections are added only when there are few chapters.
export function outlineTitles(hierarchy, documentId) {
  const roots = hierarchy.filter((node) => !documentId || node.documentId === documentId)
  const titles = []
  collectTitles(roots, 0, roots.length < MIN_TOP_LEVEL_TITLES ? 1 : 0, titles)
  return titles.slice(0, MAX_OUTLINE_TITLES)
}


export function buildScopePayload(node) {
  const descendantTitles = []


  function collectTitles(currentNode) {
    for (const child of currentNode.children || []) {
      if (descendantTitles.length >= 30) break
      descendantTitles.push(child.title)
      collectTitles(child)
    }
  }

  collectTitles(node)

  return {
    id: node.id,
    title: node.title,
    type: node.type || 'section',
    documentId: node.documentId || null,
    filename: node.filename || '',
    page: node.page || null,
    pageLabel: node.pageLabel || (node.page ? `p. ${node.page}` : ''),
    summary: node.summary || '',
    excerpt: node.excerpt || '',
    descendantTitles: descendantTitles.slice(0, 30),
  }
}

