import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon, HomeIcon, ChartBarIcon, UsersIcon, PhoneIcon, ClipboardDocumentListIcon, ArrowRightOnRectangleIcon, UserIcon } from '@heroicons/react/24/outline';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Badge from '../common/Badge';
import toast from 'react-hot-toast';

/**
 * Sidebar overlay component with hamburger menu
 * @param {boolean} isOpen - Sidebar open state
 * @param {function} onClose - Close handler
 */
const Sidebar = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
    navigate('/login');
    onClose();
  };

  const menuItems = {
    kapolri: [
      { icon: HomeIcon, label: 'Voice Assistant', path: '/assistant' },
      { icon: ChartBarIcon, label: 'Dashboard', path: '/kapolri/dashboard' },
      { icon: UsersIcon, label: 'User Management', path: '/kapolri/users' },
      { icon: PhoneIcon, label: 'Contact Management', path: '/kapolri/contacts' },
      { icon: ClipboardDocumentListIcon, label: 'Audit Logs', path: '/kapolri/audit-logs' },
    ],
    kapolda: [
      { icon: HomeIcon, label: 'Voice Assistant', path: '/assistant' },
      { icon: ChartBarIcon, label: 'Dashboard', path: '/kapolda/dashboard' },
      { icon: UsersIcon, label: 'Users', path: '/kapolda/users' },
      { icon: PhoneIcon, label: 'Contact Management', path: '/kapolda/contacts' },
      { icon: ClipboardDocumentListIcon, label: 'Audit Logs', path: '/kapolda/audit-logs' },
    ],
    kapolres: [
      { icon: HomeIcon, label: 'Voice Assistant', path: '/assistant' },
      { icon: ChartBarIcon, label: 'Dashboard', path: '/kapolres/dashboard' },
      { icon: UserIcon, label: 'Profile', path: '/kapolres/profile' },
      { icon: PhoneIcon, label: 'Contacts', path: '/kapolres/contacts' },
      { icon: ClipboardDocumentListIcon, label: 'Activity Logs', path: '/kapolres/activity-logs' },
    ],
  };

  const items = menuItems[user?.role] || [];

  const handleNavigate = (path) => {
    navigate(path);
    onClose();
  };

  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-in-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in-out duration-300"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-slate-900 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-hidden">
          <div className="absolute inset-0 overflow-hidden">
            <div className="pointer-events-none fixed inset-y-0 left-0 flex max-w-full">
              <Transition.Child
                as={Fragment}
                enter="transform transition ease-in-out duration-300"
                enterFrom="-translate-x-full"
                enterTo="translate-x-0"
                leave="transform transition ease-in-out duration-300"
                leaveFrom="translate-x-0"
                leaveTo="-translate-x-full"
              >
                <Dialog.Panel className="pointer-events-auto w-screen max-w-xs">
                  <div className="flex h-full flex-col bg-white shadow-xl">
                    <div className="px-4 py-6 border-b border-slate-200">
                      <div className="flex items-center justify-between">
                        <Dialog.Title className="text-lg font-semibold text-slate-900">
                          Menu
                        </Dialog.Title>
                        <button
                          type="button"
                          className="rounded-lg p-2 hover:bg-slate-100 transition-colors"
                          onClick={onClose}
                        >
                          <XMarkIcon className="h-6 w-6 text-slate-500" />
                        </button>
                      </div>
                      
                      <div className="mt-4 flex items-center gap-3">
                        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <span className="text-blue-600 font-semibold">
                            {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-slate-900 truncate">
                            {user?.full_name || user?.username}
                          </p>
                          <Badge role={user?.role} variant="role" />
                        </div>
                      </div>
                    </div>

                    <nav className="flex-1 overflow-y-auto px-4 py-4">
                      <div className="space-y-1">
                        {items.map((item) => {
                          const Icon = item.icon;
                          const isActive = location.pathname === item.path;
                          
                          return (
                            <button
                              key={item.path}
                              onClick={() => handleNavigate(item.path)}
                              className={`
                                w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                                ${isActive 
                                  ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-600' 
                                  : 'text-slate-700 hover:bg-slate-50'
                                }
                              `}
                            >
                              <Icon className="h-5 w-5" />
                              <span>{item.label}</span>
                            </button>
                          );
                        })}
                      </div>
                    </nav>

                    <div className="border-t border-slate-200 p-4">
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
                      >
                        <ArrowRightOnRectangleIcon className="h-5 w-5" />
                        <span>Logout</span>
                      </button>
                    </div>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
};

export default Sidebar;
