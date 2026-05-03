// src/services/recetasService.js
const BASE = import.meta.env.VITE_API_URL || 'https://sweetland-by-anny-production.up.railway.app';
const API_URL = `${BASE}/recetas`;

export const recetasService = {
  async getRecetas() {
    try {
      const response = await fetch(`${API_URL}/`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error al cargar recetas');
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.getRecetas:', error);
      throw error;
    }
  },

  async getRecetasPorProducto(productoId) {
    try {
      const response = await fetch(`${API_URL}/producto/${productoId}`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error al cargar recetas del producto');
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.getRecetasPorProducto:', error);
      throw error;
    }
  },

  async getCostoProduccion(productoId) {
    try {
      const response = await fetch(`${API_URL}/costo-produccion/${productoId}`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error al calcular costo de producción');
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.getCostoProduccion:', error);
      throw error;
    }
  },

  async createReceta(recetaData) {
    try {
      const response = await fetch(`${API_URL}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(recetaData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.createReceta:', error);
      throw error;
    }
  },

  async createRecetasMultiples(productoId, ingredientes) {
    try {
      const response = await fetch(`${API_URL}/multiple`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ id_producto: productoId, ingredientes })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al crear recetas');
      }
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.createRecetasMultiples:', error);
      throw error;
    }
  },

  async updateReceta(recetaId, recetaData) {
    try {
      const response = await fetch(`${API_URL}/${recetaId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(recetaData)
      });
      if (!response.ok) throw new Error('Error al actualizar receta');
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.updateReceta:', error);
      throw error;
    }
  },

  async deleteReceta(recetaId) {
    try {
      const response = await fetch(`${API_URL}/${recetaId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Error al eliminar receta');
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.deleteReceta:', error);
      throw error;
    }
  },

  async deleteRecetasProducto(productoId) {
    try {
      const response = await fetch(`${API_URL}/producto/${productoId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Error al eliminar recetas del producto');
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.deleteRecetasProducto:', error);
      throw error;
    }
  }
};