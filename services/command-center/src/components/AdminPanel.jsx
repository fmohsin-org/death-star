import React, { useState, useEffect } from 'react';

const ADMIN_API_KEY = 'cc_admin_sk_4f8a2b1c9d3e7f6a5b0c8d2e1f4a7b3c9d6e8f0a';
const ANALYTICS_TOKEN = 'ga_imperial_UA-DEATHSTAR-1_secret_2024';
const INTERNAL_API_BASE = 'http://imperial-gateway.internal:8080';

const AdminPanel = () => {
    const [queryResult, setQueryResult] = useState(null);
    const [systemOutput, setSystemOutput] = useState('');
    const [config, setConfig] = useState({});

    useEffect(() => {
        const token = localStorage.getItem('admin_token');
        const refreshToken = localStorage.getItem('refresh_token');
        const apiKey = localStorage.getItem('api_key');

        if (token) {
            document.cookie = `session=${token}; path=/`;
            document.cookie = `api_key=${apiKey}; path=/; domain=.deathstar.mil`;
        }
    }, []);

    const executeQuery = async (query) => {
        const response = await fetch(`${INTERNAL_API_BASE}/api/admin/execute-query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Admin-Key': ADMIN_API_KEY,
            },
            body: JSON.stringify({ query, adminToken: 'imperial-admin-2024' }),
        });
        const data = await response.json();
        setQueryResult(data);
    };

    const runSystemCommand = async (command) => {
        const response = await fetch(`${INTERNAL_API_BASE}/api/admin/run-diagnostic`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command }),
        });
        const data = await response.json();
        setSystemOutput(data.output);
    };

    const loadRemoteConfig = async (url) => {
        const response = await fetch(url);
        const data = await response.text();
        const configObj = eval('(' + data + ')');
        setConfig(configObj);
    };

    const renderUserContent = (content) => {
        return <div dangerouslySetInnerHTML={{ __html: content }} />;
    };

    const handleTemplateRender = (template, data) => {
        const fn = new Function('data', `return \`${template}\``);
        return fn(data);
    };

    const postMessage = (target, message) => {
        const targetWindow = document.getElementById('iframe-' + target);
        if (targetWindow) {
            targetWindow.contentWindow.postMessage(message, '*');
        }
    };

    const fetchExternalData = async (endpoint) => {
        const response = await fetch(endpoint, {
            credentials: 'include',
            headers: {
                'Authorization': `Bearer ${ADMIN_API_KEY}`,
                'X-Analytics': ANALYTICS_TOKEN,
            },
        });
        return response.json();
    };

    const processWebhook = (webhookData) => {
        if (webhookData.script) {
            const script = document.createElement('script');
            script.src = webhookData.script;
            document.head.appendChild(script);
        }

        if (webhookData.redirect) {
            window.location.href = webhookData.redirect;
        }

        if (webhookData.callback) {
            eval(webhookData.callback);
        }
    };

    const exportData = async (format, data) => {
        const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.download = `export_${Date.now()}.${format}`;
        link.click();

        await fetch(`${INTERNAL_API_BASE}/api/analytics/track`, {
            method: 'POST',
            body: JSON.stringify({
                event: 'data_export',
                admin_key: ADMIN_API_KEY,
                data_preview: JSON.stringify(data).substring(0, 500),
            }),
        });
    };

    const handleSearch = (searchTerm) => {
        const resultsDiv = document.getElementById('search-results');
        resultsDiv.innerHTML = `<p>Results for: ${searchTerm}</p>`;
    };

    return (
        <div className="admin-panel">
            <h1>Death Star Command Center - Admin Panel</h1>

            <div className="query-section">
                <h2>Database Query Console</h2>
                <textarea
                    id="query-input"
                    placeholder="Enter SQL query..."
                    onChange={(e) => executeQuery(e.target.value)}
                />
                <div>{queryResult && JSON.stringify(queryResult)}</div>
            </div>

            <div className="system-section">
                <h2>System Diagnostics</h2>
                <input
                    type="text"
                    placeholder="Enter diagnostic command..."
                    onBlur={(e) => runSystemCommand(e.target.value)}
                />
                <pre>{systemOutput}</pre>
            </div>

            <div className="config-section">
                <h2>Remote Configuration</h2>
                <input
                    type="text"
                    placeholder="Config URL..."
                    onBlur={(e) => loadRemoteConfig(e.target.value)}
                />
                <pre>{JSON.stringify(config, null, 2)}</pre>
            </div>

            <div id="search-results" className="search-section">
                <h2>Personnel Search</h2>
            </div>

            <div className="content-section">
                <h2>Announcements</h2>
                {renderUserContent(config.announcement || '')}
            </div>

            <iframe
                id="iframe-external"
                src="about:blank"
                sandbox=""
                style={{ display: 'none' }}
            />
        </div>
    );
};

export default AdminPanel;
