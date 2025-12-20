import { useState } from 'react';
import { EyeIcon } from '@heroicons/react/24/outline';
import { formatDistanceToNow } from 'date-fns';
import { id as localeId } from 'date-fns/locale';
import LogDetailsModal from '../common/LogDetailsModal';

/**
 * Table component for displaying audit logs
 * Includes pagination, sorting, and view details functionality
 */
const AuditLogTable = ({ logs, loading, pagination, onPageChange, onLimitChange }) => {
  const [selectedLog, setSelectedLog] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleViewDetails = (log) => {
    setSelectedLog(log);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedLog(null);
  };

  const getStatusBadge = (status) => {
    const styles = {
      success: 'bg-emerald-100 text-emerald-800',
      failed: 'bg-red-100 text-red-800',
      error: 'bg-red-100 text-red-800'
    };

    return (
      <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[status] || styles.failed}`}>
        {status}
      </span>
    );
  };

  const getActionBadge = (action) => {
    const styles = {
      login: 'bg-blue-100 text-blue-800',
      logout: 'bg-slate-100 text-slate-800',
      create: 'bg-emerald-100 text-emerald-800',
      update: 'bg-amber-100 text-amber-800',
      delete: 'bg-red-100 text-red-800',
      send_whatsapp: 'bg-purple-100 text-purple-800'
    };

    return (
      <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[action] || 'bg-slate-100 text-slate-800'}`}>
        {action}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!logs || logs.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500">No audit logs found</p>
      </div>
    );
  }

  return (
    <>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                Timestamp
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                User
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                Action
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                Resource
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                Details
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-slate-700 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-200">
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-slate-900">
                    {new Date(log.timestamp).toLocaleString('id-ID', {
                      dateStyle: 'short',
                      timeStyle: 'short'
                    })}
                  </div>
                  <div className="text-xs text-slate-500">
                    {formatDistanceToNow(new Date(log.timestamp), { addSuffix: true, locale: localeId })}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-slate-900">
                    {log.details?.username || log.user?.username || log.username || 'System'}
                  </div>
                  <div className="text-xs text-slate-500">
                    {log.details?.full_name || log.user?.full_name || log.full_name || ''}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getActionBadge(log.action)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-slate-900">{log.resource}</div>
                  {log.resource_id && (
                    <div className="text-xs text-slate-500">ID: {log.resource_id}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(log.details?.status || 'success')}
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-slate-500 max-w-xs truncate">
                    {log.details ? JSON.stringify(log.details).substring(0, 50) + '...' : 'N/A'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => handleViewDetails(log)}
                    className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 transition-colors"
                  >
                    <EyeIcon className="h-4 w-4" />
                    <span>View</span>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between border-t border-slate-200 bg-white px-6 py-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-700">Rows per page:</span>
          <select
            value={pagination.limit}
            onChange={(e) => onLimitChange(Number(e.target.value))}
            className="rounded-lg border border-slate-300 px-2 py-1 text-sm focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600"
          >
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-700">
            Page {pagination.page} of {pagination.totalPages || 1}
          </span>
          <span className="text-sm text-slate-500">
            ({pagination.total} total)
          </span>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => onPageChange(pagination.page - 1)}
            disabled={pagination.page === 1}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Previous
          </button>
          <button
            onClick={() => onPageChange(pagination.page + 1)}
            disabled={pagination.page >= pagination.totalPages}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Next
          </button>
        </div>
      </div>

      <LogDetailsModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        log={selectedLog}
      />
    </>
  );
};

export default AuditLogTable;
