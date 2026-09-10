import { Link } from 'react-router-dom'
import { services, sharedLibs, scanSummary } from '../data/services'

export default function DashboardPage() {
  const totals = services.reduce(
    (acc, s) => ({
      critical: acc.critical + s.findings.critical,
      high: acc.high + s.findings.high,
      medium: acc.medium + s.findings.medium,
      low: acc.low + s.findings.low,
    }),
    { critical: 0, high: 0, medium: 0, low: 0 }
  )
  const total = totals.critical + totals.high + totals.medium + totals.low

  return (
    <div>
      <h1 className="page-title">DSOP Command Center</h1>
      <p className="page-subtitle">DS-1 Orbital Battle Station -- All Systems Operational</p>

      <div className="stats-row">
        <div className="stat-card stat-total">
          <div className="stat-value">{total}</div>
          <div className="stat-label">Total Findings</div>
        </div>
        <div className="stat-card stat-critical">
          <div className="stat-value">{totals.critical}</div>
          <div className="stat-label">Critical</div>
        </div>
        <div className="stat-card stat-high">
          <div className="stat-value">{totals.high}</div>
          <div className="stat-label">High</div>
        </div>
        <div className="stat-card stat-medium">
          <div className="stat-value">{totals.medium}</div>
          <div className="stat-label">Medium</div>
        </div>
        <div className="stat-card stat-low">
          <div className="stat-value">{totals.low}</div>
          <div className="stat-label">Low</div>
        </div>
      </div>

      <div className="section-title">Scan Coverage</div>
      <div className="stats-row">
        {Object.values(scanSummary).map(s => (
          <div key={s.label} className="stat-card">
            <div className="stat-value" style={{ fontSize: '1.4rem', color: 'var(--accent-blue)' }}>{s.count}+</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="section-title">Services ({services.length})</div>
      <div className="service-grid">
        {services.map(s => (
          <div key={s.id} className="card service-card">
            <div className="service-header">
              <div>
                <h3>{s.name}</h3>
                <span className="port">:{s.port}</span>
              </div>
              <span className={`lang-badge ${s.langClass}`}>{s.lang}</span>
            </div>
            <p className="desc">{s.desc}</p>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="status-dot dot-online" />
              <span style={{ fontSize: '0.78rem', color: 'var(--safe)' }}>OPERATIONAL</span>
            </div>
            <div className="finding-bar">
              {s.findings.critical > 0 && <span className="finding-pill pill-critical">{s.findings.critical} critical</span>}
              {s.findings.high > 0 && <span className="finding-pill pill-high">{s.findings.high} high</span>}
              {s.findings.medium > 0 && <span className="finding-pill pill-medium">{s.findings.medium} medium</span>}
              {s.findings.low > 0 && <span className="finding-pill pill-low">{s.findings.low} low</span>}
            </div>
          </div>
        ))}
      </div>

      <div className="section-title">Shared Libraries ({sharedLibs.length})</div>
      <div className="service-grid">
        {sharedLibs.map(l => (
          <div key={l.name} className="card service-card">
            <div className="service-header">
              <h3>{l.name}</h3>
              <span className={`lang-badge ${l.langClass}`}>{l.lang}</span>
            </div>
            <p className="desc">Cross-repo shared library consumed by multiple services. Contains vulnerable sinks that create cross-module taint flows.</p>
            <div className="finding-bar">
              <span className="finding-pill pill-critical">{l.findings} findings</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
