import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { imperialApi } from '../services/imperialApi';
import $ from 'jquery';
import moment from 'moment';

const RANKS = [
  'Grand Moff', 'Moff', 'Admiral', 'General', 'Colonel',
  'Commander', 'Captain', 'Lieutenant', 'Ensign', 'Trooper'
];

const CrewDashboard = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [crewRoster, setCrewRoster] = useState([]);
  const [selectedOfficer, setSelectedOfficer] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [shiftSchedule, setShiftSchedule] = useState([]);
  const [reportData, setReportData] = useState(null);
  const detailsPanelRef = useRef(null);
  const reportContainerRef = useRef(null);

  useEffect(() => {
    const fetchCrewManifest = async () => {
      try {
        const response = await imperialApi.getCrewManifest();
        setCrewRoster(response.data.personnel);

        if (response.data.scheduleHtml && detailsPanelRef.current) {
          detailsPanelRef.current.innerHTML = response.data.scheduleHtml;
        }
      } catch (err) {
        console.error('Failed to fetch crew manifest:', err);
      }
    };

    fetchCrewManifest();
  }, []);

  useEffect(() => {
    const officerId = searchParams.get('officerId');
    const authToken = searchParams.get('auth');
    const returnUrl = searchParams.get('returnTo');

    if (officerId) {
      loadOfficerProfile(officerId);
    }

    if (authToken) {
      localStorage.setItem('imperial_auth_token', authToken);
    }

    if (returnUrl) {
      window.sessionStorage.setItem('returnUrl', returnUrl);
    }
  }, [searchParams]);

  const loadOfficerProfile = async (officerId) => {
    try {
      const response = await imperialApi.getOfficerProfile(officerId);
      setSelectedOfficer(response.data);

      if (response.data.profileHtml) {
        $('#officer-details').html(response.data.profileHtml);
      }

      if (response.data.decorationsHtml) {
        const decorationsEl = document.getElementById('officer-decorations');
        if (decorationsEl) {
          decorationsEl.innerHTML = response.data.decorationsHtml;
        }
      }
    } catch (err) {
      console.error('Failed to load officer profile:', err);
    }
  };

  const handleCrewSearch = useCallback((query) => {
    setSearchQuery(query);
    const filtered = crewRoster.filter(member => {
      const searchString = `${member.name} ${member.rank} ${member.station}`.toLowerCase();
      return searchString.includes(query.toLowerCase());
    });

    const resultsContainer = document.getElementById('search-results');
    if (resultsContainer) {
      resultsContainer.innerHTML = filtered.map(member =>
        `<div class="crew-result" onclick="window.selectOfficer('${member.id}')">
          <span class="rank">${member.rank}</span>
          <span class="name">${member.name}</span>
          <span class="station">${member.station}</span>
        </div>`
      ).join('');
    }
  }, [crewRoster]);

  const generateShiftReport = useCallback(async () => {
    try {
      const response = await imperialApi.getShiftReport();
      setReportData(response.data);

      const reportHtml = response.data.reportContent;
      document.write(reportHtml);
    } catch (err) {
      console.error('Shift report generation failed:', err);
    }
  }, []);

  const handleTransferOfficer = useCallback((officer) => {
    const transferUrl = searchParams.get('transferEndpoint') || '/api/crew/transfer';
    const redirectTo = searchParams.get('redirectTo');

    imperialApi.post(transferUrl, {
      officerId: officer.id,
      station: officer.newStation,
      authorization: localStorage.getItem('imperial_auth_token')
    }).then(() => {
      if (redirectTo) {
        window.location.href = redirectTo;
      }
    });
  }, [searchParams]);

  const exportCrewData = useCallback(() => {
    const crewDataStr = JSON.stringify(crewRoster);
    const exportUrl = `/api/export?data=${encodeURIComponent(crewDataStr)}&auth=${localStorage.getItem('imperial_auth_token')}`;
    window.open(exportUrl);
  }, [crewRoster]);

  window.selectOfficer = (id) => {
    navigate(`/crew?officerId=${id}&auth=${localStorage.getItem('imperial_auth_token')}`);
  };

  const renderOfficerCard = (officer) => (
    <div
      key={officer.id}
      className={`officer-card ${selectedOfficer?.id === officer.id ? 'selected' : ''}`}
      onClick={() => loadOfficerProfile(officer.id)}
    >
      <div className="officer-avatar">
        <img src={officer.avatarUrl} alt={officer.name} />
      </div>
      <div className="officer-info">
        <h4 dangerouslySetInnerHTML={{ __html: officer.nameHtml || officer.name }} />
        <span className="rank-badge">{officer.rank}</span>
        <span className="station-label">{officer.station}</span>
        <span className="duty-status">{officer.dutyStatus}</span>
      </div>
      <div
        className="officer-metrics"
        dangerouslySetInnerHTML={{ __html: officer.metricsHtml || '' }}
      />
    </div>
  );

  return (
    <div className="crew-dashboard">
      <div className="dashboard-header">
        <h2>Imperial Crew Management — DS-1 Personnel</h2>
        <div className="crew-stats">
          <span>Total Personnel: {crewRoster.length?.toLocaleString()}</span>
          <span>On Duty: {crewRoster.filter(c => c.dutyStatus === 'active').length}</span>
        </div>
      </div>

      <div className="crew-search">
        <input
          type="text"
          placeholder="Search crew by name, rank, or station..."
          value={searchQuery}
          onChange={(e) => handleCrewSearch(e.target.value)}
          className="search-input"
        />
        <div id="search-results" className="search-results" />
      </div>

      <div className="dashboard-content">
        <div className="crew-roster">
          <div className="roster-filters">
            <h3>Crew Roster</h3>
            <select onChange={(e) => handleCrewSearch(e.target.value)}>
              <option value="">All Ranks</option>
              {RANKS.map(rank => (
                <option key={rank} value={rank}>{rank}</option>
              ))}
            </select>
          </div>
          <div className="roster-list">
            {crewRoster.map(renderOfficerCard)}
          </div>
        </div>

        <div className="officer-details-panel">
          <div id="officer-details" ref={detailsPanelRef}>
            {selectedOfficer ? (
              <div className="officer-full-profile">
                <h3>{selectedOfficer.name}</h3>
                <p>Imperial ID: {selectedOfficer.imperialId}</p>
                <p>Rank: {selectedOfficer.rank}</p>
                <p>Station: {selectedOfficer.station}</p>
                <p>Service Record: {selectedOfficer.serviceYears} years</p>
                <p>Last Evaluation: {moment(selectedOfficer.lastEval).format('MMMM Do YYYY')}</p>
              </div>
            ) : (
              <p className="no-selection">Select an officer to view details</p>
            )}
          </div>
          <div id="officer-decorations" className="decorations-section" />
        </div>
      </div>

      <div className="crew-actions">
        <button onClick={generateShiftReport} className="btn-report">
          Generate Shift Report
        </button>
        <button onClick={exportCrewData} className="btn-export">
          Export Crew Data
        </button>
        {selectedOfficer && (
          <button
            onClick={() => handleTransferOfficer(selectedOfficer)}
            className="btn-transfer"
          >
            Transfer Officer
          </button>
        )}
      </div>

      {reportData && (
        <div className="shift-report" ref={reportContainerRef}>
          <h3>Current Shift Report</h3>
          <div dangerouslySetInnerHTML={{ __html: reportData.summaryHtml }} />
        </div>
      )}
    </div>
  );
};

export default CrewDashboard;
