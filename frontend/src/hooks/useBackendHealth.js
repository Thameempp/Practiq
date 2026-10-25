import { useEffect, useState } from 'react'


export function useBackendHealth(apiUrl) {
  const [online, setOnline] = useState(true)
  useEffect(() => {
    let mounted = true
    let controller = null


    async function check() {
      controller?.abort()
      const request = new AbortController()
      controller = request
      const timeout = setTimeout(() => request.abort(), 2500)
      try {
        const response = await fetch(`${apiUrl}/health`, { signal: request.signal, cache: 'no-store' })
        if (mounted) {
          setOnline(response.ok)
        }
      } catch {
        if (mounted) {
          setOnline(false)
        }
      } finally {
        clearTimeout(timeout)
      }
    }
    check()
    const interval = setInterval(check, 4000)
    return () => {
      mounted = false
      clearInterval(interval)
      controller?.abort()
    }
  }, [apiUrl])
  return [online, setOnline]
}
