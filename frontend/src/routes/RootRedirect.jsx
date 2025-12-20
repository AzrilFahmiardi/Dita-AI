import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * Smart redirect component for root path
 * Redirects to login if not authenticated, or to /assistant (default landing page) if authenticated
 */
const RootRedirect = () => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  // All authenticated users go to assistant page (default landing page)
  return <Navigate to="/assistant" replace />;
};

export default RootRedirect;
