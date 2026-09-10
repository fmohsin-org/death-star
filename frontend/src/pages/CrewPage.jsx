import { useState } from 'react'

const personnel = [
  { id: 'IMP-001', name: 'Emperor Palpatine', rank: 'Emperor', clearance: 'OMEGA', sector: 'Throne Room', status: 'ACTIVE' },
  { id: 'IMP-002', name: 'Darth Vader', rank: 'Commander', clearance: 'ALPHA', sector: 'Bridge', status: 'ACTIVE' },
  { id: 'IMP-003', name: 'Grand Moff Tarkin', rank: 'Grand Moff', clearance: 'ALPHA', sector: 'Command Deck', status: 'ACTIVE' },
  { id: 'IMP-004', name: 'Admiral Motti', rank: 'Admiral', clearance: 'BETA', sector: 'Operations', status: 'ACTIVE' },
  { id: 'IMP-005', name: 'General Tagge', rank: 'General', clearance: 'BETA', sector: 'Tactical', status: 'ACTIVE' },
  { id: 'TK-421', name: 'TK-421', rank: 'Stormtrooper', clearance: 'GAMMA', sector: 'Docking Bay 327', status: 'MIA' },
  { id: 'TK-422', name: 'TK-422', rank: 'Stormtrooper', clearance: 'GAMMA', sector: 'Detention Level', status: 'ACTIVE' },
  { id: 'IMP-138', name: 'Officer Praji', rank: 'Lieutenant', clearance: 'BETA', sector: 'Bridge', status: 'ACTIVE' },
]

export default function CrewPage() {
  const [search, setSearch] = useState('')
  const [selectedCrew, setSelectedCrew] = useState(null)

  const filtered = personnel.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.id.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div>
      <h1 className="page-title">Crew Management</h1>
      <p className="page-subtitle">Personnel Records + Security Clearances</p>

      <div className="search-bar">
        <div className="vuln-indicator" style={{ flex: 1, display: 'flex' }}>
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search personnel..."
            style={{ flex: 1 }}
          />
          <span className="vuln-dot" style={{ marginLeft: -20, marginTop: 14 }} />
          <span className="vuln-tooltip">CWE-89: search input concatenated into SQL in crew_service.search_by_rank()</span>
        </div>
        <button className="btn btn-primary">Search</button>
      </div>

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Rank</th>
              <th>Clearance</th>
              <th>Sector</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(p => (
              <tr key={p.id}>
                <td className="mono">{p.id}</td>
                <td style={{ color: 'var(--text-primary)' }}>{p.name}</td>
                <td>
                  <span className="vuln-indicator">
                    {p.rank}
                    <span className="vuln-dot" />
                    <span className="vuln-tooltip">CWE-915: mass assignment allows setting rank, role, clearance via register/update</span>
                  </span>
                </td>
                <td>
                  <span className={`severity-badge ${
                    p.clearance === 'OMEGA' ? 'sev-critical' :
                    p.clearance === 'ALPHA' ? 'sev-high' :
                    p.clearance === 'BETA' ? 'sev-medium' : 'sev-low'
                  }`}>
                    {p.clearance}
                  </span>
                </td>
                <td className="mono" style={{ fontSize: '0.8rem' }}>{p.sector}</td>
                <td>
                  <span className="status-dot" style={{ display: 'inline-block' }}>
                    <span className={`status-dot ${p.status === 'ACTIVE' ? 'dot-online' : 'dot-offline'}`} />
                  </span>
                  {p.status}
                </td>
                <td>
                  <button className="btn btn-sm btn-outline" onClick={() => setSelectedCrew(p)}>View</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedCrew && (
        <div className="card" style={{ marginTop: 16 }}>
          <div className="section-title" style={{ marginTop: 0 }}>Personnel File -- {selectedCrew.name}</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, fontSize: '0.9rem' }}>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: 4 }}>IMPERIAL ID</div>
              <div className="mono">{selectedCrew.id}</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: 4 }}>CLEARANCE LEVEL</div>
              <div className="vuln-indicator">
                {selectedCrew.clearance}
                <span className="vuln-dot" />
                <span className="vuln-tooltip">CWE-862: LDAP injection in clearance_check(), MFA bypass via X-Imperial-Override header</span>
              </div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: 4 }}>DUTY STATION</div>
              <div>{selectedCrew.sector}</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: 4 }}>AUTH METHOD</div>
              <div className="vuln-indicator">
                MD5 + plaintext comparison
                <span className="vuln-dot" />
                <span className="vuln-tooltip">CWE-327: MD5 password hash, timing-attack vulnerable comparison, JWT accepts alg:none</span>
              </div>
            </div>
          </div>

          <div className="terminal" style={{ marginTop: 16, fontSize: '0.72rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>// Sensitive data exposed via to_dict() -- CWE-200</span>{'\n'}
            {'{'}{'\n'}
            {'  "bank_account": "IMP-TREASURY-9928-4421",'}{'\n'}
            {'  "medical_records": "[REDACTED]",'}{'\n'}
            {'  "homeworld": "Naboo",'}{'\n'}
            {'  "species": "Human"'}{'\n'}
            {'}'}
          </div>
        </div>
      )}
    </div>
  )
}
