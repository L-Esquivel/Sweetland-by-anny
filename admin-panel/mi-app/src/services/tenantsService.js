const BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';
const API_URL = `${BASE.replace(/\/$/, '')}/tenants`;

export const tenantsService = {
  async getAllTenants() {
    try {
      const response = await fetch(`${API_URL}/`, { credentials: 'include' });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'No tienes permiso para ver esta sección');
      }
      return await response.json();
    } catch (error) {
      throw error;
    }
  },

  async createTenant(data) {
    try {
      const response = await fetch(`${API_URL}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      const responseData = await response.json();
      if (!response.ok) {
        throw new Error(responseData.error || 'Error al crear el tenant');
      }
      return responseData;
    } catch (error) {
      throw error;
    }
  },

  async updateTenant(id, data) {
    try {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      const responseData = await response.json();
      if (!response.ok) {
        throw new Error(responseData.error || 'Error al actualizar el tenant');
      }
      return responseData;
    } catch (error) {
      throw error;
    }
  },

  async deleteTenant(id) {
    const response = await fetch(`${API_URL}/${id}`, { method: 'DELETE', credentials: 'include' });
    const responseData = await response.json();
    if (!response.ok) throw new Error(responseData.error || 'Error al eliminar el tenant');
    return responseData;
  },
};