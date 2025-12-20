import api from './api';

const roleService = {
  getAllRoles: async () => {
    const response = await api.get('/api/roles');
    return response;
  },

  updatePermissions: async (roleId, permissions) => {
    const response = await api.put(`/api/roles/${roleId}/permissions`, { permissions });
    return response;
  },
};

export default roleService;
