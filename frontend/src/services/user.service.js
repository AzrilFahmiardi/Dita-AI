import api from './api';

/**
 * User management service
 * Handles all user-related API calls
 */
const userService = {
  /**
   * Fetch all users with optional filters
   * @param {Object} params - Query parameters
   * @param {string} params.role - Filter by role
   * @param {boolean} params.is_active - Filter by status
   * @returns {Promise<Array>} List of users
   */
  getUsers: async (params = {}) => {
    const response = await api.get('/api/users', { params });
    return response;
  },

  /**
   * Get user by ID
   * @param {number} id - User ID
   * @returns {Promise<Object>} User object
   */
  getUserById: async (id) => {
    const response = await api.get(`/api/users/${id}`);
    return response;
  },

  /**
   * Create new user
   * @param {Object} userData - User data
   * @param {string} userData.nrp - User NRP
   * @param {string} userData.username - Username
   * @param {string} userData.password - Password
   * @param {string} userData.full_name - Full name
   * @param {string} userData.role - User role
   * @param {boolean} userData.is_active - Active status
   * @returns {Promise<Object>} Created user
   */
  createUser: async (userData) => {
    const response = await api.post('/api/users', userData);
    return response;
  },

  /**
   * Update existing user
   * @param {number} id - User ID
   * @param {Object} userData - Updated user data
   * @returns {Promise<Object>} Updated user
   */
  updateUser: async (id, userData) => {
    const response = await api.put(`/api/users/${id}`, userData);
    return response;
  },

  /**
   * Delete user
   * @param {number} id - User ID
   * @returns {Promise<void>}
   */
  deleteUser: async (id) => {
    await api.delete(`/api/users/${id}`);
  },

  /**
   * Toggle user active status
   * @param {number} id - User ID
   * @param {boolean} isActive - New active status
   * @returns {Promise<Object>} Updated user
   */
  toggleUserStatus: async (id, isActive) => {
    const response = await api.put(`/api/users/${id}`, { is_active: isActive });
    return response;
  },

  /**
   * Change user password
   * @param {number} id - User ID
   * @param {string} newPassword - New password
   * @returns {Promise<Object>} Success message
   */
  changePassword: async (id, newPassword) => {
    const response = await api.post(`/api/users/${id}/change-password`, {
      new_password: newPassword
    });
    return response;
  }
};

export default userService;
