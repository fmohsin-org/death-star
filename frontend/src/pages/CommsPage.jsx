import { useState } from 'react'

const messages = [
  { id: 'MSG-7721', from: 'Emperor Palpatine', to: 'Lord Vader', classification: 'TOP SECRET', channel: 'HOLONET-ALPHA', time: '14:32:01', preview: 'Execute Order 66 contingency protocols for...' },
  { id: 'MSG-7720', from: 'Grand Moff Tarkin', to: 'Admiral Motti', classification: 'SECRET', channel: 'COMMAND-NET', time: '14:28:45', preview: 'Superlaser test firing scheduled for 1600...' },
  { id: 'MSG-7719', from: 'Comms Officer', to: 'All Stations', classification: 'RESTRICTED', channel: 'BROADCAST', time: '14:15:22', preview: 'Shield generator maintenance window 0200-0400...' },
  { id: 'MSG-7718', from: 'ISB Agent', to: 'Security Detail', classification: 'TOP SECRET', channel: 'ISB-SECURE', time: '13:55:10', preview: 'Rebel infiltration suspected in Sector 7G...' },
  { id: 'MSG-7717', from: 'Docking Control', to: 'Bay 327', classification: 'UNCLASSIFIED', channel: 'OPS-NET', time: '13:42:33', preview: 'Incoming freighter YT-1300 requesting landing...' },
  { id: 'MSG-7716', from: 'Engineering', to: 'Life Support', classification: 'RESTRICTED', channel: 'ENGINEERING', time: '13:30:00', preview: 'Thermal exhaust port ventilation readings anomalous...' },
]

const channels = [
  { name: 'HOLONET-ALPHA', status: 'ENCRYPTED', protocol: 'AES-256-GCM', connected: 4 },
  { name: 'COMMAND-NET', status: 'ENCRYPTED', protocol: 'DES-ECB', connected: 12 },
  { name: 'ISB-SECURE', status: 'ENCRYPTED', protocol: 'DES-ECB', connected: 3 },
  { name: 'BROADCAST', status: 'CLEARTEXT', protocol: 'NONE', connected: 847 },
  { name: 'OPS-NET', status: 'CLEARTEXT', protocol: 'NONE', connected: 156 },
]

export default function CommsPage() {
  const [selectedMsg, setSelectedMsg] = useState(null)

  return (
    <div>
      <h1 className="page-title">Comms Relay</h1>
      <p className="page-subtitle">Encrypted Communications + Signal Intelligence</p>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
        <div>
          <div className="card">
            <div className="section-title" style={{ marginTop: 0 }}>
              <span className="vuln-indicator">
                Message Queue
                <span className="vuln-dot" />
                <span className="vuln-tooltip">CWE-943: $where NoSQL injection in Message.findByOfficer()</span>
              </span>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>From</th>
                  <th>Classification</th>
                  <th>Channel</th>
                  <th>Time</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {messages.map(m => (
                  <tr key={m.id}>
                    <td className="mono">{m.id}</td>
                    <td style={{ color: 'var(--text-primary)' }}>{m.from}</td>
                    <td>
                      <span className={`severity-badge ${
                        m.classification === 'TOP SECRET' ? 'sev-critical' :
                        m.classification === 'SECRET' ? 'sev-high' :
                        m.classification === 'RESTRICTED' ? 'sev-medium' : 'sev-low'
                      }`}>
                        {m.classification}
                      </span>
                    </td>
                    <td className="mono" style={{ fontSize: '0.78rem' }}>{m.channel}</td>
                    <td className="mono" style={{ fontSize: '0.78rem' }}>{m.time}</td>
                    <td>
                      <button className="btn btn-sm btn-outline" onClick={() => setSelectedMsg(m)}>View</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {selectedMsg && (
            <div className="card" style={{ marginTop: 16 }}>
              <div className="section-title" style={{ marginTop: 0 }}>Message {selectedMsg.id}</div>
              <div style={{ fontSize: '0.85rem', lineHeight: 1.6 }}>
                <div><span style={{ color: 'var(--text-muted)' }}>From:</span> {selectedMsg.from}</div>
                <div><span style={{ color: 'var(--text-muted)' }}>To:</span> {selectedMsg.to}</div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Channel:</span>{' '}
                  <span className="vuln-indicator">
                    {selectedMsg.channel}
                    <span className="vuln-dot" />
                    <span className="vuln-tooltip">CWE-79: message content rendered via ejs.render(user_template) -- SSTI</span>
                  </span>
                </div>
                <div style={{ marginTop: 12, color: 'var(--text-primary)' }}>{selectedMsg.preview}</div>
              </div>
            </div>
          )}
        </div>

        <div>
          <div className="card">
            <div className="section-title" style={{ marginTop: 0 }}>Relay Channels</div>
            {channels.map(c => (
              <div key={c.name} style={{ marginBottom: 12, padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-primary)' }}>{c.name}</span>
                  <span style={{ fontSize: '0.7rem', color: c.status === 'ENCRYPTED' ? 'var(--accent-teal)' : 'var(--danger)' }}>
                    {c.status}
                  </span>
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2 }}>
                  <span className="vuln-indicator">
                    Protocol: {c.protocol}
                    {c.protocol === 'DES-ECB' && <span className="vuln-dot" />}
                    {c.protocol === 'DES-ECB' && <span className="vuln-tooltip">CWE-327: DES-ECB with hardcoded key (cryptoService.js)</span>}
                  </span>
                  {' '} | {c.connected} connected
                </div>
              </div>
            ))}
          </div>

          <div className="card" style={{ marginTop: 16 }}>
            <div className="section-title" style={{ marginTop: 0 }}>
              <span className="vuln-indicator">
                Auth Middleware
                <span className="vuln-dot" />
                <span className="vuln-tooltip">CWE-347: JWT accepts alg:none, prototype pollution via _.merge, clearance bypassed in dev</span>
              </span>
            </div>
            <div className="terminal" style={{ fontSize: '0.72rem', maxHeight: 150 }}>
              <span style={{ color: 'var(--danger)' }}>// Hardcoded in auth.js</span>{'\n'}
              JWT_SECRET = "imperial-comms-jwt-2024"{'\n'}
              BACKUP_SECRET = "backup-imperial-key"{'\n'}
              ADMIN_BYPASS = "IMP-ADMIN-OVERRIDE-2024"{'\n'}
              {'\n'}
              <span style={{ color: 'var(--danger)' }}>// Algorithm confusion</span>{'\n'}
              accepts: ["HS256", "RS256", "none"]{'\n'}
            </div>
          </div>

          <div className="card" style={{ marginTop: 16 }}>
            <div className="section-title" style={{ marginTop: 0 }}>Encryption Keys Endpoint</div>
            <div className="terminal" style={{ fontSize: '0.72rem', maxHeight: 150 }}>
              <span style={{ color: 'var(--danger)' }}>GET /api/comms/encryption/keys</span>{'\n'}
              <span style={{ color: 'var(--text-muted)' }}>// Returns ALL keys to any caller</span>{'\n'}
              {'{'}{'\n'}
              {'  "masterKey": "imp_master_...",\n'}
              {'  "iv": "0000000000000000",\n'}
              {'  "jwtSecret": "imperial-comms...",\n'}
              {'  "privateKey": "-----BEGIN RSA..."\n'}
              {'}'}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
