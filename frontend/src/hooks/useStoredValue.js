import { useEffect, useState } from 'react'
import { readStoredValue, writeStoredValue } from '../services/browserStorage.js'


export function useStoredValue(key, fallback) {
  const [value, setValue] = useState(() => readStoredValue(key, fallback))
  useEffect(() => {
    writeStoredValue(key, value)
  }, [key, value])
  return [value, setValue]
}
