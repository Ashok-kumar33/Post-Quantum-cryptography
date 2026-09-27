import { useState } from 'react'
import Dashboard from './components/Dashboard'
import OperationsPanel from './components/OperationsPanel'
import LogConsole from './components/LogConsole'
import { useSessionSocket } from './hooks/useSessionSocket'

export default function App() {
  const { logs, connected } = useSessionSocket()
  const [localLogs, setLocalLogs] = useState([])

  function addLog(msg) {
    setLocalLogs((prev) => [...prev.slice(-199), msg])
  }

  return (
    <div style={{ maxWidth: 900, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h1>QuantumSafe Enterprise VPN Gateway</h1>
      <Dashboard connected={connected} />
      <OperationsPanel onLog={addLog} />
      <LogConsole logs={[...logs, ...localLogs]} />
    </div>
  )
}
