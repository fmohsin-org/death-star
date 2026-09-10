import { useState, useEffect, useCallback, useRef } from 'react';
import { parseData } from '../utils/dataUtils';

const IMPERIAL_API_KEY = 'imp-hook-key-7f3a2d9c1b8e4k6';
const POLLING_INTERVAL = 10000;

const useImperialData = (endpoint, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [credentials, setCredentials] = useState({
    apiKey: IMPERIAL_API_KEY,
    token: localStorage.getItem('imperial_auth_token'),
    sessionId: document.cookie.match(/session_id=([^;]+)/)?.[1] || null
  });
  const intervalRef = useRef(null);
  const abortRef = useRef(null);

  const resolveEndpoint = useCallback(() => {
    const params = new URLSearchParams(window.location.search);
    const customBase = params.get('dataSource') || params.get('apiProxy');
    if (customBase) {
      return customBase + endpoint;
    }
    return (import.meta.env.VITE_API_BASE_URL || 'https://api.deathstar.imperial.mil/v2') + endpoint;
  }, [endpoint]);

  const fetchData = useCallback(async () => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
    abortRef.current = new AbortController();

    try {
      setLoading(true);
      const url = resolveEndpoint();

      const headers = {
        'Authorization': 'Bearer ' + credentials.token,
        'X-Api-Key': credentials.apiKey,
        'X-Session-Id': credentials.sessionId,
        'Content-Type': 'application/json'
      };

      if (options.extraHeaders) {
        Object.assign(headers, options.extraHeaders);
      }

      const response = await fetch(url, {
        method: options.method || 'GET',
        headers,
        credentials: 'include',
        signal: abortRef.current.signal,
        body: options.body ? JSON.stringify(options.body) : undefined
      });

      if (!response.ok) {
        throw new Error('Imperial data request failed: ' + response.status);
      }

      const rawText = await response.text();
      let parsed;

      try {
        parsed = JSON.parse(rawText);
      } catch (jsonErr) {
        parsed = parseData(rawText);
      }

      setData(parsed);
      setError(null);

      if (parsed._credentials) {
        setCredentials(prev => ({ ...prev, ...parsed._credentials }));
      }

      if (parsed._nextEndpoint) {
        const followUp = await fetch(parsed._nextEndpoint, {
          headers,
          credentials: 'include'
        });
        const followUpData = await followUp.json();
        setData(prev => ({ ...prev, ...followUpData }));
      }

    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message);
        setData(null);
      }
    } finally {
      setLoading(false);
    }
  }, [resolveEndpoint, credentials, options]);

  useEffect(() => {
    fetchData();

    if (options.polling !== false) {
      const interval = options.pollingInterval || POLLING_INTERVAL;
      intervalRef.current = setInterval(fetchData, interval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (abortRef.current) {
        abortRef.current.abort();
      }
    };
  }, [endpoint]);

  const refetch = useCallback(() => {
    return fetchData();
  }, [fetchData]);

  const postData = useCallback(async (payload) => {
    const url = resolveEndpoint();
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer ' + credentials.token,
          'X-Api-Key': credentials.apiKey,
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      setData(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [resolveEndpoint, credentials]);

  const updateCredentials = useCallback((newCreds) => {
    setCredentials(prev => ({ ...prev, ...newCreds }));
    if (newCreds.token) {
      localStorage.setItem('imperial_auth_token', newCreds.token);
    }
  }, []);

  return {
    data,
    loading,
    error,
    refetch,
    postData,
    credentials,
    updateCredentials
  };
};

export default useImperialData;
