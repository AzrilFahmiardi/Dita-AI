import { useState, useEffect } from 'react';
import { 
  FunnelIcon, 
  ArrowPathIcon,
  ArrowDownTrayIcon 
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import useAuditLogs from '../hooks/useAuditLogs';
import AuditLogTable from '../components/tables/AuditLogTable';
import toast from 'react-hot-toast';

/**
 * Audit Logs page
 * View and filter system audit logs with export functionality
 * Data is scoped based on user role and permissions
 */
const AuditLogs = () => {
  const { hasPermission } = useAuth();
  const { logs, loading, pagination, fetchLogs, exportLogs } = useAuditLogs();
  const [filters, setFilters] = useState({
    action: '',
    resource: '',
    days: ''
  });
  const [isFilterExpanded, setIsFilterExpanded] = useState(true);

  useEffect(() => {
    fetchLogs(filters, 1, 10);
  }, []);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleApplyFilters = () => {
    fetchLogs(filters, 1, pagination.limit);
  };

  const handleResetFilters = () => {
    const resetFilters = {
      action: '',
      resource: '',
      days: ''
    };
    setFilters(resetFilters);
    fetchLogs(resetFilters, 1, pagination.limit);
  };

  const handleExport = () => {
    exportLogs(filters);
  };

  const handlePageChange = (newPage) => {
    fetchLogs(filters, newPage, pagination.limit);
  };

  const handleLimitChange = (newLimit) => {
    fetchLogs(filters, 1, newLimit);
  };

  const actionTypes = [
    'login',
    'logout',
    'create',
    'update',
    'delete',
    'send_whatsapp'
  ];

  const resourceTypes = [
    'auth',
    'user',
    'contact',
    'user_contact'
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-end">
        {hasPermission('export_data') && (
          <button
            onClick={handleExport}
            className="inline-flex items-center gap-2 rounded-lg bg-white border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <ArrowDownTrayIcon className="h-4 w-4" />
            <span>Export CSV</span>
          </button>
        )}
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
        <div className="border-b border-slate-200 px-6 py-4">
          <button
            onClick={() => setIsFilterExpanded(!isFilterExpanded)}
            className="flex items-center gap-2 text-sm font-medium text-slate-700 hover:text-slate-900 transition-colors"
          >
            <FunnelIcon className="h-4 w-4" />
            <span>Filters</span>
            <span className="text-xs text-slate-500">
              ({Object.values(filters).filter(v => v !== '').length} active)
            </span>
          </button>
        </div>

        {isFilterExpanded && (
          <div className="px-6 py-4 border-b border-slate-200">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Action
                </label>
                <select
                  value={filters.action}
                  onChange={(e) => handleFilterChange('action', e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600"
                >
                  <option value="">All Actions</option>
                  {actionTypes.map((action) => (
                    <option key={action} value={action}>
                      {action}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Resource Type
                </label>
                <select
                  value={filters.resource}
                  onChange={(e) => handleFilterChange('resource', e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600"
                >
                  <option value="">All Resources</option>
                  {resourceTypes.map((resource) => (
                    <option key={resource} value={resource}>
                      {resource}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Time Period
                </label>
                <select
                  value={filters.days}
                  onChange={(e) => handleFilterChange('days', e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600"
                >
                  <option value="">All Time</option>
                  <option value="1">Last 24 Hours</option>
                  <option value="7">Last 7 Days</option>
                  <option value="30">Last 30 Days</option>
                  <option value="90">Last 90 Days</option>
                </select>
              </div>
            </div>

            <div className="flex gap-3 mt-4">
              <button
                onClick={handleApplyFilters}
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
              >
                <FunnelIcon className="h-4 w-4" />
                <span>Apply Filters</span>
              </button>
              <button
                onClick={handleResetFilters}
                className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
              >
                <ArrowPathIcon className="h-4 w-4" />
                <span>Reset</span>
              </button>
            </div>
          </div>
        )}

        <AuditLogTable
          logs={logs}
          loading={loading}
          pagination={pagination}
          onPageChange={handlePageChange}
          onLimitChange={handleLimitChange}
        />
      </div>
    </div>
  );
};

export default AuditLogs;
