import api from './api';
import config from '../config/config';

/**
 * Authentication service
 * Handles login, logout, and token refresh operations
 */
const authService = {
  /**
   * Login user with credentials
   * @param {string} username - User username
   * @param {string} password - User password
   * @returns {Promise<Object>} User data and tokens
   */
  login: async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (response.access_token) {
      localStorage.setItem(config.tokenKey, response.access_token);
      localStorage.setItem(config.refreshTokenKey, response.refresh_token);
      localStorage.setItem(config.userKey, JSON.stringify(response.user));
    }

    return response;
  },

  /**
   * Logout current user
   */
  logout: () => {
    localStorage.removeItem(config.tokenKey);
    localStorage.removeItem(config.refreshTokenKey);
    localStorage.removeItem(config.userKey);
  },

  /**
   * Get current user from localStorage
   * @returns {Object|null} User data
   */
  getCurrentUser: () => {
    const userStr = localStorage.getItem(config.userKey);
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Check if user is authenticated
   * @returns {boolean}
   */
  isAuthenticated: () => {
    return !!localStorage.getItem(config.tokenKey);
  },

  /**
   * Refresh access token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise<Object>} New access token
   */
  refresh: async (refreshToken) => {
    const response = await api.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response;
  },
};

export default authService;
