import { Children } from 'react'


export function MarkdownTable({ children }) {
  const sections = Children.toArray(children)
  const body = sections.find((section) => section.type === 'tbody')
  const rows = body ? Children.toArray(body.props.children) : []

  return (
    <div className="markdown-table-list">
      {rows.map((row, rowIndex) => {
        const cells = Children.toArray(row.props.children)

        return (
          <section className="markdown-table-item" key={rowIndex}>
            {cells.map((cell, cellIndex) => (
              <div className="markdown-table-field" key={cellIndex}>
                <div>{cell.props.children}</div>
              </div>
            ))}
          </section>
        )
      })}
    </div>
  )
}

