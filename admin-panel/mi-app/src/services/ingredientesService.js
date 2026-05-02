const API_URL = 'http://localhost:5000';

export const ingredientesService = {
  // Obtener todos los ingredientes
  async getIngredientes() {
    try {
      const response = await fetch(`${API_URL}/ingredientes`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Error al cargar ingredientes');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en ingredientesService.getIngredientes:', error);
      throw error;
    }
  },

  // Crear nuevo ingrediente
  async createIngrediente(ingredienteData) {
    try {
      const response = await fetch(`${API_URL}/ingredientes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(ingredienteData)
      });
      
      if (!response.ok) {
        throw new Error('Error al crear ingrediente');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en ingredientesService.createIngrediente:', error);
      throw error;
    }
  },

  // Actualizar ingrediente
  async updateIngrediente(ingredienteId, ingredienteData) {
    try {
      const response = await fetch(`${API_URL}/ingredientes/${ingredienteId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(ingredienteData)
      });
      
      if (!response.ok) {
        throw new Error('Error al actualizar ingrediente');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en ingredientesService.updateIngrediente:', error);
      throw error;
    }
  },

  // Eliminar ingrediente
  async deleteIngrediente(ingredienteId) {
    try {
      const response = await fetch(`${API_URL}/ingredientes/${ingredienteId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Error al eliminar ingrediente');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en ingredientesService.deleteIngrediente:', error);
      throw error;
    }
  }
};