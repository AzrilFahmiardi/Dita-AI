import api from './api';

/**
 * Contact management service
 * Handles all contact-related API calls
 */
const contactService = {
  /**
   * Fetch all contacts with optional filters
   * @param {Object} params - Query parameters
   * @param {boolean} params.is_active - Filter by status
   * @returns {Promise<Array>} List of contacts
   */
  getContacts: async (params = {}) => {
    const response = await api.get('/api/contacts', { params });
    return response;
  },

  /**
   * Get contact by ID
   * @param {number} id - Contact ID
   * @returns {Promise<Object>} Contact object with assigned users
   */
  getContactById: async (id) => {
    const response = await api.get(`/api/contacts/${id}`);
    return response;
  },

  /**
   * Create new contact
   * @param {Object} contactData - Contact data
   * @param {string} contactData.name - Contact name
   * @param {string} contactData.phone_number - Phone number (format: 628xxx)
   * @param {boolean} contactData.is_active - Active status
   * @returns {Promise<Object>} Created contact
   */
  createContact: async (contactData) => {
    const response = await api.post('/api/contacts', contactData);
    return response;
  },

  /**
   * Update existing contact
   * @param {number} id - Contact ID
   * @param {Object} contactData - Updated contact data
   * @returns {Promise<Object>} Updated contact
   */
  updateContact: async (id, contactData) => {
    const response = await api.put(`/api/contacts/${id}`, contactData);
    return response;
  },

  /**
   * Delete contact
   * @param {number} id - Contact ID
   * @returns {Promise<void>}
   */
  deleteContact: async (id) => {
    await api.delete(`/api/contacts/${id}`);
  },

  /**
   * Assign contact to user
   * @param {number} userId - User ID
   * @param {number} contactId - Contact ID
   * @param {boolean} canSend - Permission to send
   * @returns {Promise<Object>} Assignment result
   */
  assignContactToUser: async (userId, contactId, canSend = true) => {
    const response = await api.post('/api/contacts/assign', {
      user_id: userId,
      contact_id: contactId,
      can_send: canSend
    });
    return response;
  }
};

export default contactService;
