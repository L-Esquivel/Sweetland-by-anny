// 🚀 URL del backend en producción (Render)
const BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';
const API_URL = `${BASE.replace(/\/$/, '')}/ingredientes`;

export const ingredientesService = {
  async getIngredientes() {
    try {
      const response = await fetch(`${API_URL}/`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error al cargar ingredientes');
      return await response.json();
    } catch (error) {
      console.error('Error en ingredientesService.getIngredientes:', error);
      throw error;
    }
  },

  async createIngrediente(ingredienteData) {
    try {
      const response = await fetch(`${API_URL}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(ingredienteData)
      });
      
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.error || `Error del servidor: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en ingredientesService.createIngrediente:', error);
      throw error;
    }
  },

  async updateIngrediente(ingredienteId, ingredienteData) {
    try {
      const response = await fetch(`${API_URL}/${ingredienteId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(ingredienteData)
      });
      
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.error || `Error al actualizar: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en ingredientesService.updateIngrediente:', error);
      throw error;
    }
  },

  async deleteIngrediente(ingredienteId) {
    try {
      const response = await fetch(`${API_URL}/${ingredienteId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Error al eliminar ingrediente');
      return await response.json();
    } catch (error) {
      console.error('Error en ingredientesService.deleteIngrediente:', error);
      throw error;
    }
  }
};