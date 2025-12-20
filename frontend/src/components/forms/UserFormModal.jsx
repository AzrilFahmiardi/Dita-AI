import { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import Button from '../common/Button';
import Input from '../common/Input';
import userService from '../../services/user.service';
import { ROLE_IDS } from '../../utils/constants';

const UserFormModal = ({ user, onClose, onSaved }) => {
  const [formData, setFormData] = useState({
    nrp: '',
    username: '',
    password: '',
    full_name: '',
    role: 'KAPOLRES',
    is_active: true
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setFormData({
        nrp: user.nrp,
        username: user.username,
        password: '',
        full_name: user.full_name,
        role: user.role?.name || user.role,
        is_active: user.is_active
      });
    }
  }, [user]);

  const validateForm = () => {
    const newErrors = {};

    if (!formData.nrp.trim()) {
      newErrors.nrp = 'NRP is required';
    }

    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    if (!user && !formData.password) {
      newErrors.password = 'Password is required for new users';
    } else if (formData.password && formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);

      if (user) {
        // Update existing user
        const updatePayload = {
          full_name: formData.full_name,
          role_id: ROLE_IDS[formData.role],
          is_active: formData.is_active
        };

        await userService.updateUser(user.id, updatePayload);
        
        // If password is provided, change it separately
        if (formData.password) {
          await userService.changePassword(user.id, formData.password);
        }
        
        toast.success('User updated successfully');
      } else {
        // Create new user
        const createPayload = {
          nrp: formData.nrp,
          username: formData.username,
          password: formData.password,
          full_name: formData.full_name,
          role_id: ROLE_IDS[formData.role],
          is_active: formData.is_active
        };
        
        await userService.createUser(createPayload);
        toast.success('User created successfully');
      }

      onSaved();
    } catch (error) {
      console.error('Failed to save user:', error);
      
      // Handle validation errors
      if (error.response?.status === 422 && error.response?.data?.detail) {
        const details = error.response.data.detail;
        if (Array.isArray(details)) {
          const errorMsg = details.map(err => err.msg).join(', ');
          toast.error(errorMsg);
        } else {
          toast.error(details);
        }
      } else {
        const errorMessage = error.response?.data?.detail || 'Failed to save user';
        toast.error(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    if (errors[name]) {
      setErrors({ ...errors, [name]: '' });
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-50" onClick={onClose}></div>

        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-slate-900">
              {user ? 'Edit User' : 'Create New User'}
            </h3>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="NRP"
              name="nrp"
              value={formData.nrp}
              onChange={handleChange}
              error={errors.nrp}
              required
              disabled={!!user}
              title={user ? "NRP cannot be changed" : ""}
            />

            <Input
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              error={errors.username}
              required
              disabled={!!user}
              title={user ? "Username cannot be changed" : ""}
            />

            <Input
              label={user ? 'Password (leave blank to keep current)' : 'Password'}
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              error={errors.password}
              required={!user}
            />

            <Input
              label="Full Name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              error={errors.full_name}
              required
            />

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Role
              </label>
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="KAPOLRI">KAPOLRI</option>
                <option value="KAPOLDA">KAPOLDA</option>
                <option value="KAPOLRES">KAPOLRES</option>
              </select>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="is_active"
                id="is_active"
                checked={formData.is_active}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="is_active" className="ml-2 text-sm text-slate-700">
                Active
              </label>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button type="button" variant="secondary" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" loading={loading}>
                {user ? 'Update User' : 'Create User'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UserFormModal;
