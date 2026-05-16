const BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';
const API_URL = `${BASE.replace(/\/$/, '')}/platform`;

export const platformService = {
  async contactSupport(data) {
    try {
      const response = await fetch(`${API_URL}/contact-support`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      const responseData = await response.json();
      if (!response.ok) {
        throw new Error(responseData.error || 'Error sending support request');
      }
      return responseData;
    } catch (error) {
      throw error;
    }
  },

  async getPlatformStats() {
    try {
      const response = await fetch(`${API_URL}/dashboard-stats`, { credentials: 'include' });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error fetching statistics');
      }
      return await response.json();
    } catch (error) {
      throw error;
    }
  },
};