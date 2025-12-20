import { useState, useEffect } from 'react';
import {
  MagnifyingGlassIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  FunnelIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Badge from '../components/common/Badge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Card from '../components/common/Card';
import userService from '../services/user.service';
import roleService from '../services/role.service';
import UserFormModal from '../components/forms/UserFormModal';
import ConfirmDialog from '../components/common/ConfirmDialog';
import RolePermissionModal from '../components/modals/RolePermissionModal';

const UserManagement = () => {
  const { hasPermission } = useAuth();
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showUserModal, setShowUserModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);
  const [showPermissionModal, setShowPermissionModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState(null);

  useEffect(() => {
    fetchUsers();
    fetchRoles();
  }, [roleFilter, statusFilter]);

  const fetchRoles = async () => {
    try {
      const data = await roleService.getAllRoles();
      setRoles(data);
    } catch (error) {
      console.error('Failed to fetch roles:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const params = {};
      if (roleFilter) params.role = roleFilter;
      if (statusFilter !== '') params.is_active = statusFilter === 'active';
      
      const data = await userService.getUsers(params);
      setUsers(data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = () => {
    setSelectedUser(null);
    setShowUserModal(true);
  };

  const handleEditUser = (user) => {
    setSelectedUser(user);
    setShowUserModal(true);
  };

  const handleDeleteClick = (user) => {
    setUserToDelete(user);
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      await userService.deleteUser(userToDelete.id);
      toast.success('User deleted successfully');
      fetchUsers();
    } catch (error) {
      console.error('Failed to delete user:', error);
      toast.error('Failed to delete user');
    } finally {
      setShowDeleteDialog(false);
      setUserToDelete(null);
    }
  };

  const handleUserSaved = () => {
    setShowUserModal(false);
    setSelectedUser(null);
    fetchUsers();
  };

  const handleToggleStatus = async (user) => {
    try {
      await userService.toggleUserStatus(user.id, !user.is_active);
      toast.success(`User ${user.is_active ? 'deactivated' : 'activated'} successfully`);
      fetchUsers();
    } catch (error) {
      console.error('Failed to toggle user status:', error);
      toast.error('Failed to update user status');
    }
  };

  const handleEditPermissions = (role) => {
    setSelectedRole(role);
    setShowPermissionModal(true);
  };

  const handlePermissionsSaved = () => {
    toast.success('Permissions updated successfully');
    fetchRoles();
    fetchUsers();
  };

  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.nrp.toLowerCase().includes(searchQuery.toLowerCase());
    
    const userRole = user.role?.name || user.role;
    const matchesRole = !roleFilter || userRole === roleFilter;
    
    const matchesStatus =
      !statusFilter ||
      (statusFilter === 'active' && user.is_active) ||
      (statusFilter === 'inactive' && !user.is_active);
    
    return matchesSearch && matchesRole && matchesStatus;
  });

  const handleResetFilters = () => {
    setSearchQuery('');
    setRoleFilter('');
    setStatusFilter('');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-end">
        {hasPermission('manage_users') && (
          <Button onClick={handleCreateUser}>
            <PlusIcon className="w-4 h-4" />
            <span className="ml-2">Create User</span>
          </Button>
        )}
      </div>

      <Card>
        <div className="p-6 border-b">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Role Permissions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {roles.map((role) => (
              <div
                key={role.id}
                className="border rounded-lg p-4 hover:border-blue-300 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-medium text-gray-900">{role.name}</h3>
                    <p className="text-sm text-gray-600">Level {role.level}</p>
                  </div>
                  <button
                    onClick={() => handleEditPermissions(role)}
                    className="flex items-center gap-1 px-2 py-1 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded transition-colors"
                    title="Edit Permissions"
                  >
                    <Cog6ToothIcon className="w-4 h-4" />
                    <span>Edit</span>
                  </button>
                </div>
                <div className="space-y-1">
                  {role.permissions && Object.entries(role.permissions).map(([key, value]) => (
                    <div key={key} className="flex items-center text-sm">
                      <span className={`w-2 h-2 rounded-full mr-2 ${value ? 'bg-green-500' : 'bg-gray-300'}`} />
                      <span className={value ? 'text-gray-700' : 'text-gray-400'}>
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      <Card>
        <div className="space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search by username, name, or NRP..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <select
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
                className="px-3 py-2 pr-10 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Roles</option>
                <option value="KAPOLRI">KAPOLRI</option>
                <option value="KAPOLDA">KAPOLDA</option>
                <option value="KAPOLRES">KAPOLRES</option>
              </select>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 pr-10 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>

              {(searchQuery || roleFilter || statusFilter) && (
                <Button variant="ghost" onClick={handleResetFilters}>
                  Reset
                </Button>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-700">
                  NRP
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-700">
                  Username
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-700">
                  Full Name
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-700">
                  Role
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-700">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-700">
                  Last Login
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-slate-700">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-4 py-8 text-center text-slate-500">
                    No users found
                  </td>
                </tr>
              ) : (
                filteredUsers.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-sm text-slate-700">{user.nrp}</td>
                    <td className="px-4 py-3 text-sm font-medium text-slate-900">
                      {user.username}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-700">
                      {user.full_name}
                    </td>
                    <td className="px-4 py-3">
                      <Badge role={user.role?.name || user.role} />
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleToggleStatus(user)}
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full transition-colors ${
                          user.is_active
                            ? 'bg-green-100 text-green-700 hover:bg-green-200'
                            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                        }`}
                      >
                        {user.is_active ? 'Active' : 'Inactive'}
                      </button>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-700">
                      {user.last_login
                        ? new Date(user.last_login).toLocaleDateString()
                        : 'Never'}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex justify-end gap-2">
                        {hasPermission('manage_users') && (
                          <button
                            onClick={() => handleEditUser(user)}
                            className="p-1 text-blue-600 hover:text-blue-800"
                            title="Edit user"
                          >
                            <PencilIcon className="w-5 h-5" />
                          </button>
                        )}
                        {hasPermission('manage_users') && (
                          <button
                            onClick={() => handleDeleteClick(user)}
                            className="p-1 text-red-600 hover:text-red-800"
                            title="Delete user"
                          >
                            <TrashIcon className="w-5 h-5" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="mt-4 flex items-center justify-between text-sm text-slate-600">
          <p>
            Showing {filteredUsers.length} of {users.length} users
          </p>
        </div>
      </Card>

      {showUserModal && (
        <UserFormModal
          user={selectedUser}
          onClose={() => {
            setShowUserModal(false);
            setSelectedUser(null);
          }}
          onSaved={handleUserSaved}
        />
      )}

      {showDeleteDialog && (
        <ConfirmDialog
          title="Delete User"
          message={`Are you sure you want to delete user "${userToDelete?.username}"? This action cannot be undone.`}
          confirmLabel="Delete"
          onConfirm={handleDeleteConfirm}
          onCancel={() => {
            setShowDeleteDialog(false);
            setUserToDelete(null);
          }}
          danger
        />
      )}

      {showPermissionModal && (
        <RolePermissionModal
          role={selectedRole}
          onClose={() => {
            setShowPermissionModal(false);
            setSelectedRole(null);
          }}
          onSuccess={handlePermissionsSaved}
        />
      )}
    </div>
  );
};

export default UserManagement;
