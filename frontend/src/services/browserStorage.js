export function readStoredValue(key, fallback, storage) {
  try {
    const value = JSON.parse((storage ?? localStorage).getItem(key))
    if (Array.isArray(fallback)) return Array.isArray(value) ? value : fallback
    return value && typeof value === 'object' && !Array.isArray(value) ? value : fallback
  } catch {
    return fallback
  }
}


export function writeStoredValue(key, value, storage) {
  try {
    const target = storage ?? localStorage
    if (value == null || Array.isArray(value) && !value.length) target.removeItem(key)
    else target.setItem(key, JSON.stringify(value))
  } catch { /* Storage does not determine whether the workspace is usable. */ }
}
