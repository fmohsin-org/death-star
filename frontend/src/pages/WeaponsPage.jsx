import { useState } from 'react'

const targets = [
  { id: 'ALD-001', name: 'Alderaan', sector: 'SECTOR-7G', status: 'LOCKED', threat: 'HIGH', coords: '35.2, -42.7' },
  { id: 'YAV-004', name: 'Yavin IV', sector: 'SECTOR-12', status: 'SCANNING', threat: 'CRITICAL', coords: '12.8, 67.3' },
  { id: 'HOT-003', name: 'Hoth', sector: 'SECTOR-19', status: 'STANDBY', threat: 'LOW', coords: '-89.1, 15.6' },
  { id: 'END-002', name: 'Endor', sector: 'SECTOR-42', status: 'STANDBY', threat: 'MEDIUM', coords: '45.0, -22.4' },
]

const shieldSectors = [
  { sector: 'NORTH', strength: 97, status: 'ACTIVE' },
  { sector: 'SOUTH', strength: 94, status: 'ACTIVE' },
  { sector: 'EAST', strength: 89, status: 'DEGRADED' },
  { sector: 'WEST', strength: 96, status: 'ACTIVE' },
]

export default function WeaponsPage() {
  const [selectedTarget, setSelectedTarget] = useState(null)
  const [firingLog, setFiringLog] = useState([])

  const fireSuperLaser = () => {
    if (!selectedTarget) return
    setFiringLog(prev => [
      ...prev,
      `[${new Date().toISOString()}] SUPERLASER FIRED at ${selectedTarget.name} (${selectedTarget.coords})`,
    ])
  }

  return (
    <div>
      <h1 className="page-title">Weapons Control</h1>
      <p className="page-subtitle">Superlaser Targeting + Shield Management</p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
        <div className="card">
          <div className="section-title" style={{ marginTop: 0 }}>Targeting Computer</div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Target</th>
                <th>Sector</th>
                <th>Threat</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {targets.map(t => (
                <tr key={t.id}>
                  <td>
                    <span className="mono">{t.id}</span>
                    <br />
                    <span style={{ color: 'var(--text-primary)' }}>{t.name}</span>
                  </td>
                  <td>
                    <span className="vuln-indicator">
                      <span className="mono">{t.sector}</span>
                      <span className="vuln-dot" />
                      <span className="vuln-tooltip">CWE-78: sector param injected into shell command in targeting.go:SetTarget()</span>
                    </span>
                  </td>
                  <td>
                    <span className={`severity-badge sev-${t.threat.toLowerCase()}`}>{t.threat}</span>
                  </td>
                  <td style={{ color: t.status === 'LOCKED' ? 'var(--danger)' : 'var(--text-muted)' }}>{t.status}</td>
                  <td>
                    <button className="btn btn-sm btn-outline" onClick={() => setSelectedTarget(t)}>Select</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <div className="section-title" style={{ marginTop: 0 }}>Deflector Shields</div>
          {shieldSectors.map(s => (
            <div key={s.sector} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
              <span style={{ width: 50, fontSize: '0.8rem', color: 'var(--text-muted)' }}>{s.sector}</span>
              <div style={{ flex: 1, background: 'var(--bg-input)', borderRadius: 4, height: 20, overflow: 'hidden' }}>
                <div style={{
                  width: `${s.strength}%`,
                  height: '100%',
                  background: s.status === 'DEGRADED' ? 'var(--warning)' : 'var(--accent-teal)',
                  transition: 'width 0.3s',
                }} />
              </div>
              <span className="mono" style={{ fontSize: '0.8rem', width: 40 }}>{s.strength}%</span>
              <span className="vuln-indicator">
                <span className={`status-dot ${s.status === 'ACTIVE' ? 'dot-online' : 'dot-warning'}`} />
                <span className="vuln-tooltip">CWE-89: sector query param in SQL string (shields.go)</span>
              </span>
            </div>
          ))}

          <div className="section-title">Override Codes</div>
          <div className="terminal" style={{ fontSize: '0.75rem', maxHeight: 120 }}>
            <span style={{ color: 'var(--danger)' }}>// Hardcoded in shields.go</span>{'\n'}
            PALPATINE-66-EXECUTE{'\n'}
            VADER-OVERRIDE-501ST{'\n'}
            TARKIN-DOCTRINE-ALPHA{'\n'}
          </div>
        </div>
      </div>

      {selectedTarget && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="section-title" style={{ marginTop: 0 }}>Firing Control -- {selectedTarget.name}</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 16 }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>TARGET ID</span>
              <div className="mono">{selectedTarget.id}</div>
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>COORDINATES</span>
              <div className="vuln-indicator">
                <span className="mono">{selectedTarget.coords}</span>
                <span className="vuln-dot" />
                <span className="vuln-tooltip">CWE-78: coords interpolated into exec.Command shell string</span>
              </div>
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>POWER LEVEL</span>
              <div className="vuln-indicator">
                <span className="mono">100%</span>
                <span className="vuln-dot" />
                <span className="vuln-tooltip">CWE-190: integer overflow in CalculatePowerOutput (superlaser.go)</span>
              </div>
            </div>
          </div>
          <button className="btn btn-danger" onClick={fireSuperLaser}>FIRE SUPERLASER</button>
        </div>
      )}

      {firingLog.length > 0 && (
        <div className="terminal">
          {firingLog.map((l, i) => <div key={i}>{l}</div>)}
        </div>
      )}
    </div>
  )
}
