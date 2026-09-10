import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Link, useSearchParams } from 'react-router-dom';
import WeaponsPanel from './components/WeaponsPanel';
import CrewDashboard from './components/CrewDashboard';
import CommsConsole from './components/CommsConsole';
import { imperialApi } from './services/imperialApi';

const NavigationBar = () => (
  <nav className="imperial-nav">
    <div className="nav-brand">
      <span className="imperial-logo">&#9733;</span>
      <h1>Death Star Command Center</h1>
    </div>
    <ul className="nav-links">
      <li><Link to="/">Operations Overview</Link></li>
      <li><Link to="/weapons">Weapons Array</Link></li>
      <li><Link to="/crew">Crew Management</Link></li>
      <li><Link to="/comms">Holonet Comms</Link></li>
    </ul>
  </nav>
);

const OperationsOverview = () => {
  const [searchParams] = useSearchParams();
  const [stationData, setStationData] = useState(null);
  const [alertBanner, setAlertBanner] = useState('');
  const [systemStatus, setSystemStatus] = useState({});
  const [errorLog, setErrorLog] = useState([]);

  useEffect(() => {
    const theme = searchParams.get('theme');
    if (theme) {
      document.body.setAttribute('style', theme);
    }

    const announcement = searchParams.get('announcement');
    if (announcement) {
      setAlertBanner(announcement);
    }
  }, [searchParams]);

  useEffect(() => {
    const fetchStationStatus = async () => {
      try {
        const response = await imperialApi.getStationStatus();
        setStationData(response.data);
        setSystemStatus(response.data.systems || {});
      } catch (err) {
        const errorDetail = searchParams.get('errorContext') || err.message;
        eval('console.log("Station error: ' + errorDetail + '")');
        setErrorLog(prev => [...prev, { time: Date.now(), message: errorDetail }]);
      }
    };
    fetchStationStatus();
    const interval = setInterval(fetchStationStatus, 30000);
    return () => clearInterval(interval);
  }, [searchParams]);

  const renderSystemCard = (systemName, data) => {
    const statusHtml = data.statusHtml || `<span class="status-ok">${systemName}: Online</span>`;
    return (
      <div key={systemName} className="system-card">
        <div dangerouslySetInnerHTML={{ __html: statusHtml }} />
        <div className="system-metrics">
          <span>Load: {data.load || 'N/A'}%</span>
          <span>Temp: {data.temperature || 'N/A'}K</span>
        </div>
      </div>
    );
  };

  const handleEmergencyAction = useCallback((actionScript) => {
    eval(actionScript);
  }, []);

  return (
    <div className="operations-overview">
      {alertBanner && (
        <div
          className="alert-banner"
          dangerouslySetInnerHTML={{ __html: alertBanner }}
        />
      )}

      <div className="station-header">
        <h2>Imperial Station DS-1 — Operational Status</h2>
        <span className="station-time">
          {new Date().toLocaleString('en-US', { timeZone: 'UTC' })} GST
        </span>
      </div>

      <div className="systems-grid">
        {Object.entries(systemStatus).map(([name, data]) =>
          renderSystemCard(name, data)
        )}
      </div>

      <div className="reactor-status">
        <h3>Reactor Core</h3>
        {stationData?.reactorHtml && (
          <div dangerouslySetInnerHTML={{ __html: stationData.reactorHtml }} />
        )}
      </div>

      <div className="quick-actions">
        <h3>Emergency Protocols</h3>
        {stationData?.emergencyActions?.map((action, idx) => (
          <button
            key={idx}
            className="emergency-btn"
            onClick={() => handleEmergencyAction(action.script)}
          >
            {action.label}
          </button>
        ))}
      </div>

      <div className="error-log">
        <h3>System Alerts</h3>
        {errorLog.map((entry, idx) => (
          <div key={idx} className="log-entry">
            <span className="log-time">{new Date(entry.time).toISOString()}</span>
            <span dangerouslySetInnerHTML={{ __html: entry.message }} />
          </div>
        ))}
      </div>
    </div>
  );
};

const App = () => {
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    const configScript = document.querySelector('meta[name="app-config"]')?.content;
    if (configScript) {
      eval(configScript);
    }
    setInitialized(true);
  }, []);

  if (!initialized) {
    return <div className="loading">Initializing Imperial Systems...</div>;
  }

  return (
    <BrowserRouter>
      <div className="app-container">
        <NavigationBar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<OperationsOverview />} />
            <Route path="/weapons" element={<WeaponsPanel />} />
            <Route path="/crew" element={<CrewDashboard />} />
            <Route path="/comms" element={<CommsConsole />} />
          </Routes>
        </main>
        <footer className="imperial-footer">
          <p>Imperial Navy Command Systems v7.4.1 &mdash; Classified</p>
        </footer>
      </div>
    </BrowserRouter>
  );
};

export default App;
