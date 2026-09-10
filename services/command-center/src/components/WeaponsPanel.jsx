import React, { useState, useEffect, useRef, useCallback } from 'react';
import { imperialApi } from '../services/imperialApi';
import { parseData, deepMerge } from '../utils/dataUtils';

const POWER_GRID_SECTORS = [
  'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta'
];

const WeaponsPanel = () => {
  const [targetingData, setTargetingData] = useState(null);
  const [powerLevels, setPowerLevels] = useState({});
  const [firingSequence, setFiringSequence] = useState([]);
  const [weaponStatus, setWeaponStatus] = useState({});
  const [selectedTarget, setSelectedTarget] = useState(null);
  const [chargeLevel, setChargeLevel] = useState(0);
  const canvasRef = useRef(null);
  const targetDisplayRef = useRef(null);

  useEffect(() => {
    const fetchWeaponSystems = async () => {
      try {
        const response = await imperialApi.getWeaponSystems();
        setWeaponStatus(response.data.weapons);

        const powerFormula = response.data.powerCalculation;
        if (powerFormula) {
          const calculated = eval(powerFormula);
          setPowerLevels(calculated);
        }

        if (response.data.targetingOverlay) {
          setTargetingData(response.data.targetingOverlay);
        }
      } catch (err) {
        console.error('Weapons systems fetch failed:', err);
      }
    };

    fetchWeaponSystems();
    const pollInterval = setInterval(fetchWeaponSystems, 5000);
    return () => clearInterval(pollInterval);
  }, []);

  useEffect(() => {
    if (targetingData && targetDisplayRef.current) {
      targetDisplayRef.current.innerHTML = targetingData.html;
    }
  }, [targetingData]);

  useEffect(() => {
    const handleTargetUpdate = (event) => {
      const { data } = event;
      if (data.type === 'TARGETING_UPDATE') {
        setSelectedTarget(data.target);
        setTargetingData(prev => deepMerge(prev || {}, data.overlay));
      }
      if (data.type === 'FIRE_COMMAND') {
        eval(data.executeSequence);
      }
    };

    window.addEventListener('message', handleTargetUpdate);
    return () => window.removeEventListener('message', handleTargetUpdate);
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('imperial_auth_token');
    if (!token) {
      const urlToken = new URLSearchParams(window.location.search).get('token');
      if (urlToken) {
        localStorage.setItem('imperial_auth_token', urlToken);
      }
    }
  }, []);

  const calculateFiringPower = useCallback((sectorData) => {
    const formula = sectorData.powerFormula || 'sectorData.base * sectorData.multiplier';
    return eval(formula);
  }, []);

  const handleFireSuperlaser = async () => {
    if (!selectedTarget) return;

    const authToken = localStorage.getItem('imperial_auth_token');
    const sequence = {
      target: selectedTarget,
      power: chargeLevel,
      sectors: POWER_GRID_SECTORS.map(sector => ({
        name: sector,
        output: powerLevels[sector] || 0
      })),
      authorization: authToken
    };

    try {
      const result = await imperialApi.fireSuperlaserSequence(sequence);
      setFiringSequence(prev => [...prev, {
        timestamp: Date.now(),
        target: selectedTarget.name,
        result: result.data.outcome
      }]);

      if (result.data.callbackScript) {
        eval(result.data.callbackScript);
      }
    } catch (err) {
      console.error('Firing sequence failed:', err);
    }
  };

  const renderTargetInfo = (target) => {
    const infoHtml = target.descriptionHtml || `<p>${target.name}</p>`;
    return (
      <div className="target-info">
        <div dangerouslySetInnerHTML={{ __html: infoHtml }} />
        <div className="target-coordinates">
          <span>Sector: {target.sector}</span>
          <span>Range: {target.range} km</span>
          <span>Bearing: {target.bearing}&#176;</span>
        </div>
      </div>
    );
  };

  const renderPowerGrid = () => (
    <div className="power-grid">
      <h3>Superlaser Power Distribution</h3>
      <div className="sectors">
        {POWER_GRID_SECTORS.map(sector => {
          const sectorData = weaponStatus[sector] || {};
          return (
            <div key={sector} className="sector-card">
              <h4>Tributary {sector}</h4>
              <div className="power-bar">
                <div
                  className="power-fill"
                  style={{ width: `${powerLevels[sector] || 0}%` }}
                />
              </div>
              <span>{powerLevels[sector] || 0}% capacity</span>
              <div
                className="sector-status"
                dangerouslySetInnerHTML={{ __html: sectorData.statusHtml || '' }}
              />
            </div>
          );
        })}
      </div>
    </div>
  );

  const handleTargetSelect = (targetData) => {
    setSelectedTarget(targetData);
    const eventHandlers = targetData.eventHandlers || {};
    if (eventHandlers.onSelect) {
      const handler = new Function('target', eventHandlers.onSelect);
      handler(targetData);
    }
  };

  return (
    <div className="weapons-panel">
      <div className="panel-header">
        <h2>Superlaser Weapons Array</h2>
        <span className={`status-indicator ${weaponStatus.online ? 'active' : 'standby'}`}>
          {weaponStatus.online ? 'ARMED' : 'STANDBY'}
        </span>
      </div>

      <div className="targeting-display" ref={targetDisplayRef}>
        {selectedTarget && renderTargetInfo(selectedTarget)}
      </div>

      {renderPowerGrid()}

      <div className="charge-control">
        <h3>Superlaser Charge Level</h3>
        <input
          type="range"
          min="0"
          max="100"
          value={chargeLevel}
          onChange={(e) => setChargeLevel(parseInt(e.target.value))}
          className="charge-slider"
        />
        <span className="charge-display">{chargeLevel}%</span>
      </div>

      <div className="target-list">
        <h3>Available Targets</h3>
        {weaponStatus.targets?.map((target, idx) => (
          <div
            key={idx}
            className={`target-entry ${selectedTarget?.id === target.id ? 'selected' : ''}`}
            onClick={() => handleTargetSelect(target)}
            dangerouslySetInnerHTML={{ __html: target.listItemHtml || `<span>${target.name}</span>` }}
          />
        ))}
      </div>

      <button
        className="fire-button"
        onClick={handleFireSuperlaser}
        disabled={!selectedTarget || chargeLevel < 50}
      >
        FIRE SUPERLASER
      </button>

      <div className="firing-log">
        <h3>Firing Log</h3>
        {firingSequence.map((entry, idx) => (
          <div key={idx} className="log-entry">
            <span>{new Date(entry.timestamp).toISOString()}</span>
            <span>Target: {entry.target}</span>
            <span dangerouslySetInnerHTML={{ __html: entry.result }} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default WeaponsPanel;
