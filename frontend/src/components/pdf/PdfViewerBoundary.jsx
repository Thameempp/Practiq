import { Component } from 'react'
import { PdfViewerDialog } from './PdfViewerDialog.jsx'

export class PdfViewerBoundary extends Component {
  state = { failed: false }


  static getDerivedStateFromError() {
    return { failed: true }
  }


  render() {
    if (!this.state.failed) return this.props.children
    return <PdfViewerDialog onClose={this.props.onClose}>
      <div className="pdf-error" role="alert">
        <p>The PDF viewer could not load. Reload the page, then open the source again.</p>
        <button type="button" onClick={() => window.location.reload()}>Reload page</button>
      </div>
    </PdfViewerDialog>
  }
}
