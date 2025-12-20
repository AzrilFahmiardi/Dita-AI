import { useState, useCallback } from 'react';
import auditService from '../services/audit.service';
import toast from 'react-hot-toast';

/**
 * Custom hook for managing audit logs
 * Handles fetching, filtering, and pagination of audit logs
 */
const useAuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    limit: 10,
    totalPages: 0
  });

  /**
   * Fetch audit logs with filters
   * @param {Object} filters - Filter parameters
   * @param {number} page - Current page
   * @param {number} limit - Items per page
   */
  const fetchLogs = useCallback(async (filters = {}, page = 1, limit = 10) => {
    setLoading(true);
    setError(null);

    try {
      const params = {
        action: filters.action || undefined,
        resource: filters.resource || undefined,
        days: filters.days || undefined,
        skip: (page - 1) * limit,
        limit: limit
      };

      const response = await auditService.getAuditLogs(params);
      
      const logsData = response?.items || [];
      setLogs(logsData);
      
      setPagination({
        total: response?.total || 0,
        page: response?.page || page,
        limit: response?.limit || limit,
        totalPages: response?.total_pages || 0
      });
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to fetch audit logs';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Fetch single audit log details
   * @param {number} id - Audit log ID
   */
  const fetchLogById = useCallback(async (id) => {
    try {
      const log = await auditService.getAuditLogById(id);
      return log;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to fetch log details';
      toast.error(errorMessage);
      throw err;
    }
  }, []);

  /**
   * Export audit logs to CSV
   * @param {Object} filters - Current filter parameters
   */
  const exportLogs = useCallback(async (filters = {}) => {
    try {
      const blob = await auditService.exportAuditLogs(filters);
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `audit_logs_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('Audit logs exported successfully');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to export audit logs';
      toast.error(errorMessage);
    }
  }, []);

  return {
    logs,
    loading,
    error,
    pagination,
    fetchLogs,
    fetchLogById,
    exportLogs
  };
};

export default useAuditLogs;
