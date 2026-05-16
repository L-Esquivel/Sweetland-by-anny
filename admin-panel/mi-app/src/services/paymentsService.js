const BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';
const API_URL = `${BASE.replace(/\/$/, '')}/payments`;

export const paymentsService = {
  getPaymentsForTenant: async (tenantId) => {
    try {
      const response = await fetch(`${API_URL}/tenant/${tenantId}`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading payments');
      return await response.json();
    } catch (error) {
      console.error('Error in paymentsService.getPaymentsForTenant:', error);
      throw error;
    }
  },

  addPayment: async (paymentData) => {
    try {
      const response = await fetch(`${API_URL}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(paymentData),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error registering payment');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in paymentsService.addPayment:', error);
      throw error;
    }
  },

  deletePayment: async (paymentId) => {
    try {
      const response = await fetch(`${API_URL}/${paymentId}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error deleting payment');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in paymentsService.deletePayment:', error);
      throw error;
    }
  },
};