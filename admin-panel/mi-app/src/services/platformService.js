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
        throw new Error(responseData.error || 'Error al enviar la solicitud de soporte');
      }
      return responseData;
    } catch (error) {
      throw error;
    }
  },
};