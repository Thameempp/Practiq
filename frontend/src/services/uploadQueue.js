// A failed upload must not stop subsequent files or overlap another batch.
export function createUploadQueue(upload) {
  let tail = Promise.resolve()
  return (file) => {
    const result = tail.then(() => upload(file))
    tail = result.catch(() => {})
    return result
  }
}
