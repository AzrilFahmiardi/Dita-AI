import api from './api';

/**
 * Audit log service
 * Handles all audit log-related API calls
 */
const auditService = {
  /**
   * Fetch audit logs with optional filters
   * @param {Object} params - Query parameters
   * @param {string} params.action - Filter by action type
   * @param {string} params.resource - Filter by resource type
   * @param {number} params.days - Filter by last N days
   * @param {number} params.skip - Pagination skip
   * @param {number} params.limit - Limit results
   * @returns {Promise<Array>} List of audit logs
   */
  getAuditLogs: async (params = {}) => {
    const response = await api.get('/api/audit-logs', { params });
    return response;
  },

  /**
   * Get audit log by ID
   * @param {number} id - Audit log ID
   * @returns {Promise<Object>} Audit log details
   */
  getAuditLogById: async (id) => {
    const response = await api.get(`/api/audit-logs/${id}`);
    return response;
  },

  /**
   * Get audit logs for current user
   * @param {Object} params - Query parameters
   * @returns {Promise<Array>} List of user's audit logs
   */
  getMyAuditLogs: async (params = {}) => {
    const response = await api.get('/api/audit-logs/me', { params });
    return response;
  },

  /**
   * Export audit logs to CSV
   * @param {Object} params - Query parameters (same as getAuditLogs)
   * @returns {Promise<Blob>} CSV file blob
   */
  exportAuditLogs: async (params = {}) => {
    const response = await api.get('/api/audit-logs/export', {
      params,
      responseType: 'blob'
    });
    return response;
  }
};

export default auditService;
