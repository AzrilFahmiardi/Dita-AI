import { createContext, useState, useContext, useEffect } from 'react';
import authService from '../services/auth.service';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    console.log('AuthContext: Loaded user from localStorage:', currentUser);
    setUser(currentUser);
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    const response = await authService.login(username, password);
    console.log('AuthContext: Setting user after login:', response.user);
    setUser(response.user);
    return response;
  };

  const logout = async () => {
    await authService.logout();
    console.log('AuthContext: User logged out');
    setUser(null);
  };

  const hasPermission = (permission) => {
    if (!user || !user.role) {
      return false;
    }
    
    // If permissions object doesn't exist or is empty, fallback to role-based check
    // KAPOLRI (level 1) gets all permissions by default
    if (!user.role.permissions || Object.keys(user.role.permissions).length === 0) {
      console.warn('AuthContext: No permissions found, using role-based fallback');
      return user.role.name === 'KAPOLRI' || user.role === 'KAPOLRI';
    }
    
    return user.role.permissions[permission] === true;
  };

  const value = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
    loading,
    hasPermission,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export default AuthContext;
