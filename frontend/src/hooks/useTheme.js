import { useEffect, useState } from 'react'


export function useTheme() {
  const [theme, setTheme] = useState(() => {
    try {
      const saved = localStorage.getItem('theme')
      if (saved === 'dark' || saved === 'light') return saved
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    } catch {
      return 'light'
    }
  })
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    document.documentElement.style.colorScheme = theme
    const favicon = document.getElementById('app-favicon')
    if (favicon) {
      favicon.href = theme === 'dark' ? '/logo-dark.svg' : '/logo-light.svg'
    }
    try {
      localStorage.setItem('theme', theme)
    } catch { /* Storage is optional. */ }
  }, [theme])
  return [theme, () => setTheme((current) => current === 'dark' ? 'light' : 'dark')]
}
