import { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import Button from '../common/Button';
import Input from '../common/Input';
import contactService from '../../services/contact.service';

const ContactFormModal = ({ contact, onClose, onSaved }) => {
  const [formData, setFormData] = useState({
    name: '',
    phone_number: '',
    is_active: true
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (contact) {
      setFormData({
        name: contact.name,
        phone_number: contact.phone_number,
        is_active: contact.is_active
      });
    }
  }, [contact]);

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.phone_number.trim()) {
      newErrors.phone_number = 'Phone number is required';
    } else if (!/^628\d{8,13}$/.test(formData.phone_number)) {
      newErrors.phone_number = 'Phone number must start with 628 and be 11-16 digits';
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

      if (contact) {
        await contactService.updateContact(contact.id, formData);
        toast.success('Contact updated successfully');
      } else {
        await contactService.createContact(formData);
        toast.success('Contact created successfully');
      }

      onSaved();
    } catch (error) {
      console.error('Failed to save contact:', error);
      
      if (error.response?.status === 422 && error.response?.data?.detail) {
        const details = error.response.data.detail;
        if (Array.isArray(details)) {
          const errorMsg = details.map(err => err.msg).join(', ');
          toast.error(errorMsg);
        } else {
          toast.error(details);
        }
      } else {
        const errorMessage = error.response?.data?.detail || 'Failed to save contact';
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
              {contact ? 'Edit Contact' : 'Add New Contact'}
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
              label="Contact Name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              error={errors.name}
              required
              placeholder="Enter contact name"
            />

            <Input
              label="Phone Number"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleChange}
              error={errors.phone_number}
              required
              placeholder="628xxxxxxxxxx"
              helperText="Format: 628xxxxxxxxxx (Indonesian WhatsApp number)"
            />

            <div>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleChange}
                  className="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-slate-700">
                  Active Contact
                </span>
              </label>
              <p className="mt-1 text-xs text-slate-500">
                Inactive contacts cannot receive messages
              </p>
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="secondary"
                onClick={onClose}
                className="flex-1"
                disabled={loading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                className="flex-1"
                disabled={loading}
              >
                {loading ? 'Saving...' : contact ? 'Update' : 'Create'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ContactFormModal;
