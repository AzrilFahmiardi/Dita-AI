import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './routes/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import VoiceAssistantPage from './pages/VoiceAssistantPage';
import DashboardLayout from './components/layout/DashboardLayout';
import KapolriDashboard from './pages/kapolri/Dashboard';
import UserManagement from './pages/kapolri/UserManagement';
import ContactManagement from './pages/kapolri/ContactManagement';
import AuditLogs from './pages/kapolri/AuditLogs';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          <Route path="/assistant" element={<ProtectedRoute><VoiceAssistantPage /></ProtectedRoute>} />
          
          <Route element={<ProtectedRoute allowedRoles={['KAPOLRI']} />}>
            <Route element={<DashboardLayout />}>
              <Route path="/kapolri/dashboard" element={<KapolriDashboard />} />
              <Route path="/kapolri/users" element={<UserManagement />} />
              <Route path="/kapolri/contacts" element={<ContactManagement />} />
              <Route path="/kapolri/audit-logs" element={<AuditLogs />} />
            </Route>
          </Route>

          <Route path="/" element={<Navigate to="/assistant" replace />} />
          
          <Route path="/unauthorized" element={
            <div className="min-h-screen flex items-center justify-center bg-slate-50">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-slate-900 mb-4">403</h1>
                <p className="text-slate-600 mb-4">Unauthorized Access</p>
                <p className="text-sm text-slate-500">You do not have permission to access this page</p>
              </div>
            </div>
          } />
          
          <Route path="*" element={
            <div className="min-h-screen flex items-center justify-center bg-slate-50">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-slate-900 mb-4">404</h1>
                <p className="text-slate-600">Page not found</p>
              </div>
            </div>
          } />
        </Routes>
      </Router>
      
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#FFFFFF',
            color: '#0F172A',
            border: '1px solid #E2E8F0',
          },
          success: {
            iconTheme: {
              primary: '#10B981',
              secondary: '#FFFFFF',
            },
          },
          error: {
            iconTheme: {
              primary: '#EF4444',
              secondary: '#FFFFFF',
            },
          },
        }}
      />
    </AuthProvider>
  );
}

export default App;

