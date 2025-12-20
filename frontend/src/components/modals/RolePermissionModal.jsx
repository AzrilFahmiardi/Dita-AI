import { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import roleService from '../../services/role.service';

const PERMISSIONS = [
  { key: 'manage_users', label: 'Manage Users', description: 'Create, edit, and delete users' },
  { key: 'send_whatsapp', label: 'Send WhatsApp', description: 'Send WhatsApp broadcasts' },
  { key: 'manage_contacts', label: 'Manage Contacts', description: 'Add, edit, and delete contacts' },
  { key: 'export_data', label: 'Export Data', description: 'Export data to CSV/Excel' },
];

export default function RolePermissionModal({ role, onClose, onSuccess }) {
  const [permissions, setPermissions] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (role && role.permissions) {
      setPermissions(role.permissions);
    }
  }, [role]);

  const handleToggle = (permissionKey) => {
    setPermissions(prev => ({
      ...prev,
      [permissionKey]: !prev[permissionKey]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await roleService.updatePermissions(role.id, permissions);
      onSuccess();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update permissions');
    } finally {
      setLoading(false);
    }
  };

  if (!role) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
        <div className="flex justify-between items-center p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Edit Role Permissions</h2>
            <p className="text-sm text-gray-600 mt-1">
              Role: <span className="font-medium">{role.name}</span> (Level {role.level})
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="p-6">
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <div className="space-y-4">
              {PERMISSIONS.map((perm) => (
                <div
                  key={perm.key}
                  className="flex items-start p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center h-5 mt-0.5">
                    <input
                      type="checkbox"
                      id={perm.key}
                      checked={permissions[perm.key] || false}
                      onChange={() => handleToggle(perm.key)}
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                  </div>
                  <div className="ml-3 flex-1">
                    <label htmlFor={perm.key} className="font-medium text-gray-900 cursor-pointer">
                      {perm.label}
                    </label>
                    <p className="text-sm text-gray-600 mt-0.5">{perm.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-3 p-6 border-t bg-gray-50">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save Permissions'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
