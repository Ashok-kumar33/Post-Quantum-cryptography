import { useEffect, useRef, useState } from 'react'
import { WS_URL } from '../api/client'

export function useSessionSocket() {
  const [logs, setLogs] = useState([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'log') {
          setLogs((prev) => [...prev.slice(-199), data.message])
        }
      } catch {
        // ignore non-JSON messages
      }
    }

    return () => ws.close()
  }, [])

  return { logs, connected }
}
