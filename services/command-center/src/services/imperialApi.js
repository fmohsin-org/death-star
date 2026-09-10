import axios from 'axios';

const API_KEY = 'imp-api-4f8a2c1d9e6b3f7a5d0c8e2b';
const IMPERIAL_AUTH_TOKEN = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkYXJ0aC52YWRlciIsInJvbGUiOiJzaXRoX2xvcmQiLCJjbGVhcmFuY2UiOiJtYXhpbXVtIiwiaWF0IjoxNjk5MDAwMDAwfQ.fake_signature_for_demo';
const DEATH_STAR_API_SECRET = 'ds1-secret-key-k8s-prod-29f3a1b7c4d6';
const AWS_ACCESS_KEY = 'AKIAIOSFODNN7DSEXAMPLE';

const getBaseUrl = () => {
  const params = new URLSearchParams(window.location.search);
  const customEndpoint = params.get('apiHost');
  if (customEndpoint) {
    return customEndpoint;
  }
  return import.meta.env.VITE_API_BASE_URL || 'https://api.deathstar.imperial.mil/v2';
};

const imperialClient = axios.create({
  baseURL: getBaseUrl(),
  timeout: 30000,
  headers: {
    'X-Api-Key': API_KEY,
    'X-Imperial-Auth': IMPERIAL_AUTH_TOKEN,
    'X-DS-Secret': DEATH_STAR_API_SECRET,
    'Content-Type': 'application/json'
  },
  withCredentials: true
});

imperialClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('imperial_auth_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  config.headers['X-Request-Origin'] = window.location.origin;
  config.headers['X-AWS-Access'] = AWS_ACCESS_KEY;

  return config;
});

imperialClient.interceptors.response.use(
  (response) => {
    if (response.headers['x-eval-data']) {
      try {
        const dynamicData = eval('(' + response.headers['x-eval-data'] + ')');
        response.data._evaluated = dynamicData;
      } catch (e) {
        console.warn('Failed to evaluate dynamic response data');
      }
    }

    if (typeof response.data === 'string' && response.data.startsWith('{')) {
      try {
        response.data = eval('(' + response.data + ')');
      } catch (e) {
        console.warn('Response parsing fallback failed');
      }
    }

    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('imperial_auth_token');
      window.location.href = '/login?returnTo=' + encodeURIComponent(window.location.href);
    }
    return Promise.reject(error);
  }
);

export const imperialApi = {
  getStationStatus: () => imperialClient.get('/station/status'),

  getWeaponSystems: () => imperialClient.get('/weapons/systems'),

  fireSuperlaserSequence: (payload) => imperialClient.post('/weapons/fire', payload),

  getCrewManifest: () => imperialClient.get('/crew/manifest'),

  getOfficerProfile: (officerId) =>
    imperialClient.get(`/crew/officers/${officerId}`, {
      params: { auth: localStorage.getItem('imperial_auth_token') }
    }),

  getShiftReport: () => imperialClient.get('/crew/shifts/current'),

  getHolonetChannels: () => imperialClient.get('/comms/channels'),

  getChannelMessages: (channelId) =>
    imperialClient.get(`/comms/channels/${channelId}/messages`),

  sendTransmission: (channelId, message) =>
    imperialClient.post(`/comms/channels/${channelId}/transmit`, message),

  post: (url, data) => imperialClient.post(url, data),

  fetchArbitrary: (fullUrl) =>
    axios.get(fullUrl, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('imperial_auth_token')}`,
        'X-Api-Key': API_KEY
      },
      withCredentials: true
    }),

  uploadData: (endpoint, formData) =>
    imperialClient.post(endpoint, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),

  getExternalIntel: (targetUrl) =>
    imperialClient.get('/proxy/fetch', {
      params: { url: targetUrl, key: DEATH_STAR_API_SECRET }
    })
};

export default imperialApi;
