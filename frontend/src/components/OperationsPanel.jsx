import { useRef, useState } from 'react'
import { generateKeys, exportKeyBundle, encryptFile, decryptFile, downloadBlob } from '../api/client'

export default function OperationsPanel({ onLog }) {
  const [busy, setBusy] = useState(false)
  const encryptInput = useRef(null)
  const decryptInput = useRef(null)

  async function handleGenerate() {
    setBusy(true)
    try {
      const info = await generateKeys()
      onLog(`Keys generated: KEM pk ${info.kem_pk_size}B, DSA pk ${info.dsa_pk_size}B`)
    } catch (e) {
      onLog(`Error: ${e.message}`)
    } finally {
      setBusy(false)
    }
  }

  async function handleExport() {
    try {
      const bundle = await exportKeyBundle()
      const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' })
      downloadBlob(blob, 'enterprise_pqc_bundle.json')
    } catch (e) {
      onLog(`Error: ${e.message}`)
    }
  }

  async function handleEncrypt(e) {
    const file = e.target.files[0]
    if (!file) return
    try {
      const blob = await encryptFile(file)
      downloadBlob(blob, `${file.name}.pqsafe`)
      onLog(`Encrypted ${file.name}`)
    } catch (err) {
      onLog(`Error: ${err.message}`)
    }
    e.target.value = ''
  }

  async function handleDecrypt(e) {
    const file = e.target.files[0]
    if (!file) return
    try {
      const blob = await decryptFile(file)
      downloadBlob(blob, file.name.replace('.pqsafe', '_recovered'))
      onLog(`Decrypted ${file.name}`)
    } catch (err) {
      onLog(`Error: ${err.message}`)
    }
    e.target.value = ''
  }

  return (
    <div style={{ padding: 16, border: '1px solid #333', borderRadius: 8, marginBottom: 16 }}>
      <h2>Enterprise Operations</h2>
      <button disabled={busy} onClick={handleGenerate}>Generate Enterprise Keys</button>{' '}
      <button onClick={handleExport}>Export Key Bundle</button>{' '}
      <button onClick={() => encryptInput.current.click()}>Encrypt File</button>
      <input ref={encryptInput} type="file" hidden onChange={handleEncrypt} />{' '}
      <button onClick={() => decryptInput.current.click()}>Decrypt File</button>
      <input ref={decryptInput} type="file" hidden onChange={handleDecrypt} />
    </div>
  )
}
