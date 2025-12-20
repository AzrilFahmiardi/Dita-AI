import { useState, useEffect } from 'react';
import {
  UsersIcon,
  PhoneIcon,
  ClipboardDocumentListIcon,
  ServerIcon,
  PlusIcon
} from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import userService from '../services/user.service';
import contactService from '../services/contact.service';
import auditService from '../services/audit.service';
import { formatDistanceToNow } from 'date-fns';

const DashboardPage = () => {
  const { user, hasPermission } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  
  // Determine base path based on user role
  const basePath = user?.role === 'KAPOLRI' ? '/admin' : '/dashboard';
  
  const [stats, setStats] = useState({
    totalUsers: 0,
    usersByRole: { KAPOLRI: 0, KAPOLDA: 0, KAPOLRES: 0 },
    totalContacts: 0,
    activeContacts: 0,
    recentActivityCount: 0
  });
  const [recentActivities, setRecentActivities] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      const [users, contacts, activitiesResponse] = await Promise.all([
        userService.getUsers().catch(err => { console.error('Failed to fetch users:', err); return []; }),
        contactService.getContacts().catch(err => { console.error('Failed to fetch contacts:', err); return []; }),
        auditService.getAuditLogs({ limit: 10 }).catch(err => { console.error('Failed to fetch audit logs:', err); return { items: [] }; })
      ]);

      const activities = activitiesResponse?.items || activitiesResponse || [];

      console.log('Dashboard data loaded:', { users: users.length, contacts: contacts.length, activities: activities.length });

      const usersByRole = users.reduce((acc, user) => {
        const roleName = user.role?.name || user.role;
        acc[roleName] = (acc[roleName] || 0) + 1;
        return acc;
      }, { KAPOLRI: 0, KAPOLDA: 0, KAPOLRES: 0 });

      const activeContacts = contacts.filter(c => c.is_active).length;

      const last24Hours = new Date(Date.now() - 24 * 60 * 60 * 1000);
      const recentCount = activities.filter(
        a => a.timestamp && new Date(a.timestamp) > last24Hours
      ).length;

      setStats({
        totalUsers: users.length,
        usersByRole,
        totalContacts: contacts.length,
        activeContacts,
        recentActivityCount: recentCount
      });

      setRecentActivities(activities.slice(0, 10));
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
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
      <div className="flex items-center justify-end gap-3">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => navigate(`${basePath}/users`)}
        >
          <PlusIcon className="w-4 h-4" />
          <span className="ml-2">Create User</span>
        </Button>
        <Button
          variant="primary"
          size="sm"
          onClick={() => navigate(`${basePath}/contacts`)}
        >
          <PlusIcon className="w-4 h-4" />
          <span className="ml-2">Add Contact</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => navigate(`${basePath}/users`)}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">Total Users</p>
              <p className="text-3xl font-bold text-slate-900 mt-2">
                {stats.totalUsers}
              </p>
              <div className="mt-3 space-y-1">
                <p className="text-xs text-slate-600">
                  KAPOLRI: {stats.usersByRole.KAPOLRI}
                </p>
                <p className="text-xs text-slate-600">
                  KAPOLDA: {stats.usersByRole.KAPOLDA}
                </p>
                <p className="text-xs text-slate-600">
                  KAPOLRES: {stats.usersByRole.KAPOLRES}
                </p>
              </div>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <UsersIcon className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => navigate(`${basePath}/contacts`)}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">Total Contacts</p>
              <p className="text-3xl font-bold text-slate-900 mt-2">
                {stats.totalContacts}
              </p>
              <div className="mt-3 space-y-1">
                <p className="text-xs text-green-600">
                  Active: {stats.activeContacts}
                </p>
                <p className="text-xs text-slate-400">
                  Inactive: {stats.totalContacts - stats.activeContacts}
                </p>
              </div>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <PhoneIcon className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </Card>

        <Card
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => navigate(`${basePath}/audit-logs`)}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">Recent Activity</p>
              <p className="text-3xl font-bold text-slate-900 mt-2">
                {stats.recentActivityCount}
              </p>
              <p className="text-xs text-slate-600 mt-3">
                Actions in last 24 hours
              </p>
            </div>
            <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center">
              <ClipboardDocumentListIcon className="w-6 h-6 text-amber-600" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">System Status</p>
              <div className="mt-3 space-y-2">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <p className="text-xs text-slate-700">Database: Online</p>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <p className="text-xs text-slate-700">API: Active</p>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <p className="text-xs text-slate-700">Voice: Ready</p>
                </div>
              </div>
            </div>
            <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center">
              <ServerIcon className="w-6 h-6 text-slate-600" />
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900">Recent Activity</h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate(`${basePath}/audit-logs`)}
          >
            View All
          </Button>
        </div>

        {recentActivities.length === 0 ? (
          <p className="text-center text-slate-500 py-8">No recent activity</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-700">
                    Time
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-700">
                    User
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-700">
                    Action
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-700">
                    Resource
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-700">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {recentActivities.map((activity, index) => (
                  <tr key={activity.id || index} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-sm text-slate-700">
                      {activity.timestamp 
                        ? formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })
                        : 'N/A'
                      }
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-900">
                      {activity.details["username"] || 'System'}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-700">
                      {activity.action || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-700">
                      {activity.resource || '-'}
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-700">
                        {activity.details?.status || 'logged'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};

export default DashboardPage;
