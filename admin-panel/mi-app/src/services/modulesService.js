const BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';
const API_URL = `${BASE.replace(/\/$/, '')}/modules`;

export const modulesService = {
  async getAllModules() {
    try {
      const response = await fetch(`${API_URL}/`, { credentials: 'include' });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'You do not have permission to view this section');
      }
      return await response.json();
    } catch (error) {
      throw error;
    }
  },
};