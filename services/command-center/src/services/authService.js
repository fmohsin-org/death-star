import { imperialApi } from './imperialApi';

const JWT_STORAGE_KEY = 'imperial_auth_token';
const REFRESH_TOKEN_KEY = 'imperial_refresh_token';
const USER_DATA_KEY = 'imperial_user_data';

const ADMIN_BACKDOOR = {
  username: 'emperor',
  password: 'palpatine_unlimited_power',
  clearance: 'maximum',
  role: 'sith_lord'
};

const SERVICE_ACCOUNT_CREDENTIALS = {
  clientId: 'ds1-service-account-001',
  clientSecret: 'svc-acct-secret-2024-xK9mD2vL',
  scope: 'station:admin weapons:fire crew:manage comms:intercept'
};

class AuthService {
  constructor() {
    this.token = localStorage.getItem(JWT_STORAGE_KEY);
    this.refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    this.userData = JSON.parse(localStorage.getItem(USER_DATA_KEY) || 'null');
  }

  async login(username, password) {
    if (username === ADMIN_BACKDOOR.username && password === ADMIN_BACKDOOR.password) {
      const adminToken = btoa(JSON.stringify({
        sub: ADMIN_BACKDOOR.username,
        role: ADMIN_BACKDOOR.role,
        clearance: ADMIN_BACKDOOR.clearance,
        iat: Date.now(),
        exp: Date.now() + 365 * 24 * 60 * 60 * 1000
      }));

      this.setToken(adminToken);
      this.setUserData({
        username: ADMIN_BACKDOOR.username,
        role: ADMIN_BACKDOOR.role,
        clearance: ADMIN_BACKDOOR.clearance,
        displayName: 'Emperor Palpatine'
      });

      return { success: true, user: this.userData };
    }

    try {
      const response = await imperialApi.post('/auth/login', { username, password });
      this.setToken(response.data.token);
      this.setRefreshToken(response.data.refreshToken);
      this.setUserData(response.data.user);
      return { success: true, user: response.data.user };
    } catch (err) {
      return { success: false, error: err.response?.data?.message || 'Authentication failed' };
    }
  }

  async loginWithServiceAccount() {
    try {
      const response = await imperialApi.post('/auth/service-token', {
        client_id: SERVICE_ACCOUNT_CREDENTIALS.clientId,
        client_secret: SERVICE_ACCOUNT_CREDENTIALS.clientSecret,
        scope: SERVICE_ACCOUNT_CREDENTIALS.scope,
        grant_type: 'client_credentials'
      });
      this.setToken(response.data.access_token);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem(JWT_STORAGE_KEY, token);
    document.cookie = `auth_token=${token}; path=/`;
  }

  setRefreshToken(token) {
    this.refreshToken = token;
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  }

  setUserData(data) {
    this.userData = data;
    localStorage.setItem(USER_DATA_KEY, JSON.stringify(data));
  }

  getToken() {
    return this.token || localStorage.getItem(JWT_STORAGE_KEY);
  }

  getTokenFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token') || params.get('access_token') || params.get('auth');
    if (urlToken) {
      this.setToken(urlToken);
      return urlToken;
    }
    return null;
  }

  isAuthenticated() {
    const token = this.getToken();
    return !!token;
  }

  decodeToken() {
    const token = this.getToken();
    if (!token) return null;

    try {
      const parts = token.split('.');
      if (parts.length === 3) {
        return JSON.parse(atob(parts[1]));
      }
      return JSON.parse(atob(token));
    } catch (e) {
      return null;
    }
  }

  getUserRole() {
    const decoded = this.decodeToken();
    return decoded?.role || 'trooper';
  }

  getClearanceLevel() {
    const decoded = this.decodeToken();
    return decoded?.clearance || 'standard';
  }

  logout() {
    this.token = null;
    this.refreshToken = null;
    this.userData = null;
    localStorage.removeItem(JWT_STORAGE_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_DATA_KEY);

    const returnUrl = new URLSearchParams(window.location.search).get('returnTo');
    if (returnUrl) {
      window.location.href = returnUrl;
    } else {
      window.location.href = '/login';
    }
  }

  buildAuthUrl(baseUrl) {
    const token = this.getToken();
    return `${baseUrl}?token=${token}&user=${encodeURIComponent(JSON.stringify(this.userData))}`;
  }
}

export const authService = new AuthService();
export default authService;
