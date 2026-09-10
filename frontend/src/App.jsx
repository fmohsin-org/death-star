import { useState } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import WeaponsPage from './pages/WeaponsPage'
import CrewPage from './pages/CrewPage'
import SupplyPage from './pages/SupplyPage'
import CommsPage from './pages/CommsPage'
import InfraPage from './pages/InfraPage'
import ExploitPanel from './exploit/ExploitPanel'

export default function App() {
  const [demoMode, setDemoMode] = useState(false)
  const location = useLocation()

  const navLinks = [
    { to: '/', label: 'Command Center' },
    { to: '/weapons', label: 'Weapons' },
    { to: '/crew', label: 'Crew' },
    { to: '/supply', label: 'Supply Chain' },
    { to: '/comms', label: 'Comms' },
    { to: '/infrastructure', label: 'Infrastructure' },
  ]

  return (
    <div className="app">
      <header className="header">
        <Link to="/" className="logo">
          <span className="logo-icon">&#9678;</span> DSOP Command
        </Link>
        <nav>
          {navLinks.map(l => (
            <Link
              key={l.to}
              to={l.to}
              className={location.pathname === l.to ? 'active' : ''}
            >
              {l.label}
            </Link>
          ))}
        </nav>
        <button
          className={`demo-toggle ${demoMode ? 'active' : ''}`}
          onClick={() => setDemoMode(!demoMode)}
          title="Toggle Exploit Demo Panel"
        >
          {demoMode ? '\u{1F513}' : '\u{1F512}'}
        </button>
      </header>

      <div className="layout">
        <main className={`main ${demoMode ? 'shrunk' : ''}`}>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/weapons" element={<WeaponsPage />} />
            <Route path="/crew" element={<CrewPage />} />
            <Route path="/supply" element={<SupplyPage />} />
            <Route path="/comms" element={<CommsPage />} />
            <Route path="/infrastructure" element={<InfraPage />} />
          </Routes>
        </main>
        {demoMode && <ExploitPanel />}
      </div>
    </div>
  )
}
