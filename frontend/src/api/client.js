const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/sessions'

export async function generateKeys() {
  const res = await fetch(`${API_URL}/keys/generate`, { method: 'POST' })
  if (!res.ok) throw new Error('Key generation failed')
  return res.json()
}

export async function exportKeyBundle() {
  const res = await fetch(`${API_URL}/keys/export`)
  if (!res.ok) throw new Error('No keys to export yet')
  return res.json()
}

export async function encryptFile(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${API_URL}/files/encrypt`, { method: 'POST', body: form })
  if (!res.ok) throw new Error('Encryption failed')
  return res.blob()
}

export async function decryptFile(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${API_URL}/files/decrypt`, { method: 'POST', body: form })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || 'Decryption failed')
  }
  return res.blob()
}

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
