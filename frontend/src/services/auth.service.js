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
    const response = await api.post('/auth/login', {
      username,
      password,
    });

    if (!response.access_token) {
      throw new Error('No access token received from server');
    }

    localStorage.setItem(config.tokenKey, response.access_token);
    localStorage.setItem(config.refreshTokenKey, response.refresh_token);
    
    const userProfile = await api.get('/auth/me');
    
    if (!userProfile || !userProfile.role) {
      throw new Error('Invalid user profile received from server');
    }
    
    const userData = {
      id: userProfile.id,
      username: userProfile.username,
      role: userProfile.role, // Save full role object with permissions
      full_name: userProfile.full_name,
      nrp: userProfile.nrp,
      is_active: userProfile.is_active,
    };
    
    console.log('Login successful, user data:', userData);
    localStorage.setItem(config.userKey, JSON.stringify(userData));
    
    return { ...response, user: userData };
  },

  /**
   * Logout current user
   */
  logout: async () => {
    try {
      // Call backend logout endpoint to broadcast session event
      const token = localStorage.getItem(config.tokenKey);
      if (token) {
        await fetch(`${config.apiUrl}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
      }
    } catch (error) {
      console.error('Error calling logout endpoint:', error);
      // Continue with local cleanup even if backend call fails
    }
    
    // Clear local storage
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
    if (!userStr || userStr === 'undefined' || userStr === 'null') {
      return null;
    }
    try {
      return JSON.parse(userStr);
    } catch (error) {
      console.error('Error parsing user data:', error);
      localStorage.removeItem(config.userKey);
      return null;
    }
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
