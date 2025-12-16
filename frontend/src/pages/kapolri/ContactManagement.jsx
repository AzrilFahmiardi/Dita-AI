import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import {
  PhoneIcon,
  PencilIcon,
  TrashIcon,
  UserGroupIcon,
  PlusIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ConfirmDialog from '../../components/common/ConfirmDialog';
import contactService from '../../services/contact.service';
import ContactFormModal from '../../components/forms/ContactFormModal';
import AssignContactModal from '../../components/forms/AssignContactModal';

const ContactManagement = () => {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showContactModal, setShowContactModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedContact, setSelectedContact] = useState(null);
  const [contactToDelete, setContactToDelete] = useState(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    try {
      setLoading(true);
      const data = await contactService.getContacts();
      setContacts(data);
    } catch (error) {
      console.error('Failed to fetch contacts:', error);
      toast.error('Failed to load contacts');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateContact = () => {
    setSelectedContact(null);
    setShowContactModal(true);
  };

  const handleEditContact = (contact) => {
    setSelectedContact(contact);
    setShowContactModal(true);
  };

  const handleDeleteClick = (contact) => {
    setContactToDelete(contact);
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      await contactService.deleteContact(contactToDelete.id);
      toast.success('Contact deleted successfully');
      fetchContacts();
    } catch (error) {
      console.error('Failed to delete contact:', error);
      toast.error('Failed to delete contact');
    } finally {
      setShowDeleteDialog(false);
      setContactToDelete(null);
    }
  };

  const handleAssignContact = (contact) => {
    setSelectedContact(contact);
    setShowAssignModal(true);
  };

  const handleContactSaved = () => {
    setShowContactModal(false);
    setSelectedContact(null);
    fetchContacts();
  };

  const handleAssignmentSaved = () => {
    setShowAssignModal(false);
    setSelectedContact(null);
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setStatusFilter('');
  };

  const filteredContacts = contacts.filter((contact) => {
    const matchesSearch =
      contact.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      contact.phone_number.includes(searchQuery);

    const matchesStatus =
      !statusFilter ||
      (statusFilter === 'active' && contact.is_active) ||
      (statusFilter === 'inactive' && !contact.is_active);

    return matchesSearch && matchesStatus;
  });

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
        <Button onClick={handleCreateContact}>
          <PlusIcon className="w-4 h-4" />
          <span className="ml-2">Add Contact</span>
        </Button>
      </div>

      <Card>
        <div className="space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search by name or phone number..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 pr-10 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>

              {(searchQuery || statusFilter) && (
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
                <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700">
                  Name
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700">
                  Phone Number
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700">
                  Status
                </th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-slate-700">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {filteredContacts.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-4 py-8 text-center text-slate-500">
                    No contacts found
                  </td>
                </tr>
              ) : (
                filteredContacts.map((contact) => (
                  <tr key={contact.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <PhoneIcon className="w-4 h-4 text-slate-400" />
                        <span className="font-medium text-slate-900">
                          {contact.name}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {contact.phone_number}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          contact.is_active
                            ? 'bg-green-100 text-green-700'
                            : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {contact.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => handleAssignContact(contact)}
                          className="p-1 text-green-600 hover:text-green-800"
                          title="Assign to users"
                        >
                          <UserGroupIcon className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleEditContact(contact)}
                          className="p-1 text-blue-600 hover:text-blue-800"
                          title="Edit contact"
                        >
                          <PencilIcon className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleDeleteClick(contact)}
                          className="p-1 text-red-600 hover:text-red-800"
                          title="Delete contact"
                        >
                          <TrashIcon className="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {showContactModal && (
        <ContactFormModal
          contact={selectedContact}
          onClose={() => setShowContactModal(false)}
          onSaved={handleContactSaved}
        />
      )}

      {showAssignModal && (
        <AssignContactModal
          contact={selectedContact}
          onClose={() => setShowAssignModal(false)}
          onSaved={handleAssignmentSaved}
        />
      )}

      {showDeleteDialog && (
        <ConfirmDialog
          title="Delete Contact"
          message={`Are you sure you want to delete ${contactToDelete?.name}? This action cannot be undone.`}
          confirmText="Delete"
          onConfirm={handleDeleteConfirm}
          onCancel={() => setShowDeleteDialog(false)}
        />
      )}
    </div>
  );
};

export default ContactManagement;
