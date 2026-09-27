export default function LogConsole({ logs }) {
  return (
    <div
      style={{
        padding: 16,
        border: '1px solid #333',
        borderRadius: 8,
        background: '#000a11',
        color: '#00ff88',
        height: 240,
        overflowY: 'auto',
        fontFamily: 'monospace',
      }}
    >
      {logs.length === 0 && <div style={{ opacity: 0.6 }}>No activity yet.</div>}
      {logs.map((line, i) => (
        <div key={i}>{line}</div>
      ))}
    </div>
  )
}
