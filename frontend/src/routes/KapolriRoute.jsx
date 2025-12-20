import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * Route wrapper for KAPOLRI-only pages
 */
const KapolriRoute = ({ children }) => {
  const { user } = useAuth();

  if (user?.role?.name !== 'KAPOLRI') {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

export default KapolriRoute;
