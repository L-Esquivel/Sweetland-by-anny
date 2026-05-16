// 🚀 Backend URL
const BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';
const API_URL = `${BASE.replace(/\/$/, '')}/ingredientes`;

export const ingredientesService = {
  async getIngredients() {
    try {
      const response = await fetch(`${API_URL}/`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading ingredients');
      return await response.json();
    } catch (error) {
      console.error('Error in ingredientesService.getIngredients:', error);
      throw error;
    }
  },

  async createIngredient(ingredientData) {
    try {
      const response = await fetch(`${API_URL}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(ingredientData)
      });
      
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.error || `Server error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error in ingredientesService.createIngredient:', error);
      throw error;
    }
  },

  async updateIngredient(ingredientId, ingredientData) {
    try {
      const response = await fetch(`${API_URL}/${ingredientId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(ingredientData)
      });
      
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.error || `Error updating: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error in ingredientesService.updateIngredient:', error);
      throw error;
    }
  },

  async deleteIngredient(ingredientId) {
    try {
      const response = await fetch(`${API_URL}/${ingredientId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.error || 'Error deleting ingredient');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in ingredientesService.deleteIngredient:', error);
      throw error;
    }
  }
};