import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './routes/ProtectedRoute';
import RootRedirect from './routes/RootRedirect';
import LoginPage from './pages/LoginPage';
import VoiceAssistantPage from './pages/VoiceAssistantPage';
import DashboardLayout from './components/layout/DashboardLayout';
import DashboardPage from './pages/DashboardPage';
import UserManagement from './pages/UserManagement';
import ContactManagement from './pages/ContactManagement';
import AuditLogs from './pages/AuditLogs';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          <Route path="/assistant" element={<ProtectedRoute><VoiceAssistantPage /></ProtectedRoute>} />
          
          {/* Admin routes - KAPOLRI only (level 1) */}
          <Route element={<ProtectedRoute allowedRoles={['KAPOLRI']} />}>
            <Route element={<DashboardLayout />}>
              <Route path="/admin/dashboard" element={<DashboardPage />} />
              <Route path="/admin/users" element={<UserManagement />} />
              <Route path="/admin/contacts" element={<ContactManagement />} />
              <Route path="/admin/audit-logs" element={<AuditLogs />} />
            </Route>
          </Route>

          {/* Dashboard routes - All other roles (level 2+) */}
          <Route element={<ProtectedRoute allowedRoles={['KAPOLDA', 'KAPOLRES']} />}>
            <Route element={<DashboardLayout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/dashboard/users" element={<UserManagement />} />
              <Route path="/dashboard/contacts" element={<ContactManagement />} />
              <Route path="/dashboard/audit-logs" element={<AuditLogs />} />
            </Route>
          </Route>

          <Route path="/" element={<RootRedirect />} />
          
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

