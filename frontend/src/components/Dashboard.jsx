export default function Dashboard({ connected }) {
  return (
    <div style={{ padding: 16, border: '1px solid #333', borderRadius: 8, marginBottom: 16 }}>
      <h2>Enterprise Dashboard</h2>
      <p style={{ color: connected ? 'lime' : 'red', fontWeight: 'bold' }}>
        Status: {connected ? 'LIVE' : 'OFFLINE'}
      </p>
    </div>
  )
}
